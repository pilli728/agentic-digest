#!/usr/bin/env node
/**
 * Scrapes Twitter bookmarks using your existing Chrome login session.
 * Outputs JSON to stdout (or --output path) in the same format as bookmarks_*.json
 *
 * Usage:
 *   node scripts/fetch_bookmarks.js
 *   node scripts/fetch_bookmarks.js --output bookmarks_$(date +%Y-%m-%d).json
 *   node scripts/fetch_bookmarks.js --max 200
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const outputFlag = args.indexOf('--output');
const maxFlag = args.indexOf('--max');

const outputPath = outputFlag !== -1 ? args[outputFlag + 1] : null;
const maxBookmarks = maxFlag !== -1 ? parseInt(args[maxFlag + 1]) : 100;

// Dedicated automation profile — separate from your main Chrome profile.
// Chrome won't allow CDP/remote-debug on the default profile dir.
// This profile persists your Twitter login between runs.
const AUTOMATION_PROFILE = path.join(
  process.env.HOME,
  'Library/Application Support/Google/Chrome/AgenticEdge'
);

async function scrapeBookmarks() {
  let context;

  process.stderr.write(`Using automation profile: ${AUTOMATION_PROFILE}\n`);

  context = await chromium.launchPersistentContext(AUTOMATION_PROFILE, {
    headless: false,
    channel: 'chrome',
    args: ['--disable-blink-features=AutomationControlled'],
    timeout: 60000,
  });

  const page = await context.newPage();

  try {
    process.stderr.write('Navigating to bookmarks...\n');
    await page.goto('https://twitter.com/i/bookmarks', { waitUntil: 'networkidle', timeout: 30000 });

    // Check if we're logged in
    const url = page.url();
    if (url.includes('/login') || url.includes('/flow')) {
      process.stderr.write('ERROR: Not logged in to Twitter. Please log in first.\n');
      process.exit(1);
    }

    const bookmarks = [];
    const seen = new Set();

    async function extractTweets() {
      const tweets = await page.$$eval('article[data-testid="tweet"]', (articles) => {
        return articles.map(article => {
          // Get tweet text
          const textEl = article.querySelector('[data-testid="tweetText"]');
          const fullText = textEl ? textEl.innerText : '';

          // Get author info
          const userNameEl = article.querySelector('[data-testid="User-Name"]');
          const links = userNameEl ? userNameEl.querySelectorAll('a') : [];
          const screenName = links[1] ? links[1].href.split('/').pop() : '';
          const name = links[0] ? links[0].innerText : '';

          // Get tweet URL (timestamp link)
          const timeEl = article.querySelector('time');
          const tweetLinkEl = timeEl ? timeEl.closest('a') : null;
          const tweetUrl = tweetLinkEl ? 'https://twitter.com' + tweetLinkEl.getAttribute('href') : '';

          // Get timestamp
          const tweeted_at = timeEl ? timeEl.getAttribute('datetime') : '';

          // Get media
          const mediaEls = article.querySelectorAll('img[src*="twimg.com/media"]');
          const extended_media = Array.from(mediaEls).map(img => ({ media_url_https: img.src }));

          // Profile image
          const profileImg = article.querySelector('img[src*="profile_images"]');
          const profile_image_url_https = profileImg ? profileImg.src : '';

          return { profile_image_url_https, screen_name: screenName, name, full_text: fullText, tweeted_at, extended_media, tweet_url: tweetUrl };
        });
      });
      return tweets;
    }

    let noNewCount = 0;

    while (bookmarks.length < maxBookmarks && noNewCount < 5) {
      const tweets = await extractTweets();
      let newFound = 0;

      for (const tweet of tweets) {
        if (tweet.tweet_url && !seen.has(tweet.tweet_url)) {
          seen.add(tweet.tweet_url);
          bookmarks.push({
            bookmark_date: new Date().toISOString(),
            ...tweet,
          });
          newFound++;
        }
      }

      process.stderr.write(`  Collected ${bookmarks.length} bookmarks...\r`);

      if (newFound === 0) {
        noNewCount++;
      } else {
        noNewCount = 0;
      }

      if (bookmarks.length >= maxBookmarks) break;

      // Scroll down to load more
      await page.evaluate(() => window.scrollBy(0, window.innerHeight * 3));
      await page.waitForTimeout(1500);
    }

    process.stderr.write(`\nDone. Collected ${bookmarks.length} bookmarks.\n`);

    const json = JSON.stringify(bookmarks, null, 2);

    if (outputPath) {
      fs.writeFileSync(outputPath, json);
      process.stderr.write(`Saved to ${outputPath}\n`);
    } else {
      process.stdout.write(json);
    }

  } finally {
    await context.close();
  }
}

scrapeBookmarks().catch(err => {
  process.stderr.write(`Error: ${err.message}\n`);
  process.exit(1);
});
