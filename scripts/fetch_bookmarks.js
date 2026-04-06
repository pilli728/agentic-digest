#!/usr/bin/env node
/**
 * Scrapes Twitter bookmarks using your real Chrome via AppleScript.
 * Opens twitter.com/i/bookmarks, scrolls, extracts tweet data.
 *
 * Usage:
 *   node scripts/fetch_bookmarks.js
 *   node scripts/fetch_bookmarks.js --output bookmarks.json
 *   node scripts/fetch_bookmarks.js --max 200
 */

const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');

const args = process.argv.slice(2);
const outputFlag = args.indexOf('--output');
const maxFlag = args.indexOf('--max');
const outputPath = outputFlag !== -1 ? args[outputFlag + 1] : null;
const maxBookmarks = maxFlag !== -1 ? parseInt(args[maxFlag + 1]) : 150;

// Run AppleScript and return stdout
function as(script) {
  const tmp = `${os.tmpdir()}/bm_${Date.now()}_${Math.random().toString(36).slice(2)}.scpt`;
  fs.writeFileSync(tmp, script);
  try {
    return execSync(`osascript "${tmp}"`, { encoding: 'utf8', timeout: 30000 }).trim();
  } finally {
    try { fs.unlinkSync(tmp); } catch (_) {}
  }
}

// Execute JS in active Chrome tab — JS written to file to avoid escaping hell
function js(code) {
  const jsTmp = `${os.tmpdir()}/bm_${Date.now()}_${Math.random().toString(36).slice(2)}.js`;
  fs.writeFileSync(jsTmp, code);
  const result = as(`
set jc to do shell script "cat " & quoted form of "${jsTmp}"
tell application "Google Chrome"
  tell active tab of window 1
    return execute javascript jc
  end tell
end tell`);
  try { fs.unlinkSync(jsTmp); } catch (_) {}
  return result;
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function main() {
  // Open bookmarks in Chrome (new tab)
  process.stderr.write('Opening Twitter bookmarks in Chrome...\n');
  as(`
tell application "Google Chrome"
  activate
  if (count of windows) is 0 then
    make new window with properties {URL: "https://x.com/i/bookmarks"}
  else
    tell window 1
      make new tab with properties {URL: "https://x.com/i/bookmarks"}
    end tell
  end if
end tell`);

  process.stderr.write('Waiting for page to load (5s)...\n');
  await sleep(5000);

  // Verify we're on bookmarks
  const url = as(`tell application "Google Chrome" to return URL of active tab of window 1`);
  if (!url.includes('bookmarks')) {
    process.stderr.write(`ERROR: active tab is "${url}", not bookmarks. Focus the bookmarks tab and re-run.\n`);
    process.exit(1);
  }

  // Initialize collector on the page
  js(`window.__bm = { data: [], seen: {} };`);

  const EXTRACT = `
(function() {
  if (!window.__bm) window.__bm = { data: [], seen: {} };
  document.querySelectorAll('article[data-testid="tweet"]').forEach(function(article) {
    var timeEl = article.querySelector('time');
    var linkEl = timeEl && timeEl.closest('a');
    if (!linkEl) return;
    var href = linkEl.getAttribute('href') || '';
    var tweetUrl = href.startsWith('http') ? href : 'https://x.com' + href;
    if (window.__bm.seen[tweetUrl]) return;
    window.__bm.seen[tweetUrl] = 1;
    var textEl = article.querySelector('[data-testid="tweetText"]');
    var uEl = article.querySelector('[data-testid="User-Name"]');
    var uLinks = uEl ? uEl.querySelectorAll('a') : [];
    var profileImg = article.querySelector('img[src*="profile_images"]');
    var mediaImgs = article.querySelectorAll('img[src*="twimg.com/media"]');
    window.__bm.data.push({
      bookmark_date: new Date().toISOString(),
      profile_image_url_https: profileImg ? profileImg.src : '',
      screen_name: uLinks[1] ? uLinks[1].href.split('/').filter(Boolean).pop() : '',
      name: uLinks[0] ? uLinks[0].innerText.split('\\n')[0] : '',
      full_text: textEl ? textEl.innerText : '',
      tweeted_at: timeEl ? timeEl.getAttribute('datetime') : '',
      extended_media: Array.from(mediaImgs).map(function(img) { return { media_url_https: img.src }; }),
      tweet_url: tweetUrl
    });
  });
  return window.__bm.data.length;
})()`;

  let lastCount = 0;
  let stuckRounds = 0;

  process.stderr.write(`Scrolling and collecting (target: ${maxBookmarks})...\n`);

  while (stuckRounds < 5) {
    const countStr = js(EXTRACT);
    const count = parseInt(countStr) || 0;
    process.stderr.write(`  ${count} bookmarks...\r`);

    if (count >= maxBookmarks) break;

    if (count === lastCount) {
      stuckRounds++;
    } else {
      stuckRounds = 0;
      lastCount = count;
    }

    // Scroll down
    js(`document.documentElement.scrollTop += window.innerHeight * 3;`);
    await sleep(2000);
  }

  // Final extract pass
  js(EXTRACT);

  const jsonStr = js(`JSON.stringify(window.__bm ? window.__bm.data : [])`);
  let bookmarks;
  try {
    bookmarks = JSON.parse(jsonStr);
  } catch (e) {
    process.stderr.write(`\nFailed to parse results: ${e.message}\n`);
    process.exit(1);
  }

  process.stderr.write(`\nDone. Collected ${bookmarks.length} bookmarks.\n`);

  const output = JSON.stringify(bookmarks, null, 2);
  if (outputPath) {
    fs.writeFileSync(outputPath, output);
    process.stderr.write(`Saved to ${outputPath}\n`);
  } else {
    process.stdout.write(output + '\n');
  }
}

main().catch(err => {
  process.stderr.write(`\nError: ${err.message}\n`);
  process.exit(1);
});
