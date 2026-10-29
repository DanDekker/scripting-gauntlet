#!/usr/bin/env node
// Use browser DOM APIs against the saved page. jsdom supplies the DOM in CI.
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');

const input = process.env.IN;
const output = process.env.OUT;
if (!input || !output) throw new Error('IN and OUT are required');

const html = fs.readFileSync(path.join(input, 'pricing.html'), 'utf8');
const document = new JSDOM(html).window.document;
const table = document.querySelector('table#pricing');
if (!table) throw new Error('pricing table is missing');

const clean = cell => cell.textContent.replace(/\s+/g, ' ').trim();
const rows = [...table.querySelectorAll('tbody tr')].map(row => {
  const nameCell = row.querySelector('td.plan').cloneNode(true);
  nameCell.querySelectorAll('span.badge').forEach(badge => badge.remove());
  const name = clean(nameCell);
  const seats = Number(clean(row.querySelector('td.seats')));
  const price = Number(clean(row.querySelector('td.price')).replace(/[$,]/g, ''));
  if (!name || !Number.isInteger(seats) || !Number.isFinite(price)) {
    throw new Error('invalid pricing row');
  }
  return { name, seats, price };
});
rows.sort((a, b) => b.price - a.price || a.name.localeCompare(b.name));

const csv = value => /[",\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
const result = ['plan,seats,monthly_usd',
  ...rows.map(row => `${csv(row.name)},${row.seats},${row.price.toFixed(2)}`)
].join('\n') + '\n';
fs.mkdirSync(output, { recursive: true });
fs.writeFileSync(path.join(output, 'pricing.csv'), result);
