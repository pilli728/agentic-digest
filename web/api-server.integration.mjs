/**
 * Astro integration that auto-starts the Python API server alongside `astro dev`.
 * Uses the project's venv Python. Kills stale processes on the port if needed.
 */

import { spawn, execSync } from 'node:child_process';
import { resolve } from 'node:path';
import { existsSync } from 'node:fs';
import net from 'node:net';

const API_PORT = 8000;
const PROJECT_ROOT = resolve(import.meta.dirname, '..');

function isPortInUse(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(true));
    server.once('listening', () => { server.close(); resolve(false); });
    server.listen(port, 'localhost');
  });
}

function killStaleProcess(port) {
  try {
    const pid = execSync(`lsof -ti:${port}`, { encoding: 'utf-8' }).trim();
    if (pid) {
      console.log(`\x1b[33m[api]\x1b[0m Killing stale process ${pid} on :${port}`);
      execSync(`kill ${pid}`);
      // Brief wait for port to free up
      execSync('sleep 1');
    }
  } catch {
    // No process found or kill failed — fine either way
  }
}

function findPython() {
  // Prefer project venv
  const venvPython = resolve(PROJECT_ROOT, 'venv', 'bin', 'python3');
  if (existsSync(venvPython)) return venvPython;

  // Fallback to system
  return 'python3';
}

export default function apiServer() {
  let proc = null;

  return {
    name: 'api-server',
    hooks: {
      'astro:server:setup': async () => {
        // If port is in use, try to kill the stale process
        if (await isPortInUse(API_PORT)) {
          killStaleProcess(API_PORT);
          // Check again
          if (await isPortInUse(API_PORT)) {
            console.log(`\x1b[36m[api]\x1b[0m Port ${API_PORT} still in use — assuming API is running`);
            return;
          }
        }

        const python = findPython();
        console.log(`\x1b[36m[api]\x1b[0m Starting API server (${python})...`);

        proc = spawn(python, ['src/api_server.py'], {
          cwd: PROJECT_ROOT,
          stdio: ['ignore', 'pipe', 'pipe'],
          env: { ...process.env },
        });

        proc.stdout.on('data', (data) => {
          const line = data.toString().trim();
          if (line) console.log(`\x1b[36m[api]\x1b[0m ${line}`);
        });

        proc.stderr.on('data', (data) => {
          const line = data.toString().trim();
          if (line) console.error(`\x1b[31m[api]\x1b[0m ${line}`);
        });

        proc.on('exit', (code) => {
          if (code !== null && code !== 0) {
            console.error(`\x1b[31m[api]\x1b[0m Python API exited with code ${code}`);
          }
          proc = null;
        });

        // Wait for it to start
        await new Promise((r) => setTimeout(r, 2000));

        if (await isPortInUse(API_PORT)) {
          console.log(`\x1b[32m[api]\x1b[0m API ready at http://localhost:${API_PORT}`);
        } else {
          console.warn(`\x1b[33m[api]\x1b[0m API may not have started. Check logs above.`);
        }
      },

      'astro:server:done': () => {
        if (proc) {
          console.log(`\x1b[36m[api]\x1b[0m Stopping Python API server...`);
          proc.kill('SIGTERM');
          proc = null;
        }
      },
    },
  };
}
