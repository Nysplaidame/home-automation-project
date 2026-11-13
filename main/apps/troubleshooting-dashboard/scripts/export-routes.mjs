import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { additionalRoutes } from '../additional-routes.js';

const mainRoot = fileURLToPath(new URL('../../../', import.meta.url));
const target = path.join(mainRoot, 'docs/troubleshooting/extended-app-routes.md');
const lines = [
  '# Extended troubleshooting routes', '',
  'Generated from `main/apps/troubleshooting-dashboard/additional-routes.js`.',
  'Regenerate with `node main/apps/troubleshooting-dashboard/scripts/export-routes.mjs`.', '',
  'These read-only investigations supplement the [five original walkthroughs](diagnostic-walkthroughs.md).',
  'Keep this file in the local vault: a docker-host outage also takes the dashboard offline.',
  'This is a failure-scenario catalog, not a claim that these failures are happening now.', '',
  'Record time with timezone, source device/network, exact error and last passing layer.',
  'Collector imports cover only some signals. The other signals require the manual checks below;',
  'keep findings in operator notes. A collected step does not automatically update a check status.',
  'Keep credentials, private URLs and household data out of shared logs or incident reports.', '',
  '## Coverage', '', '| Area | Investigation |', '|---|---|',
  ...additionalRoutes.map(route => `| ${route.category} | [${route.title}](#${route.id}) |`), '',
];
for (const route of additionalRoutes) {
  lines.push(`<a id="${route.id}"></a>`, `## ${route.title}`, '', route.description, '',
    `Required evidence: ${route.checks.map(item => `${item.label} (\`${item.key}\`)`).join('; ')}.`, '');
  for (const [index, step] of route.steps.entries()) {
    lines.push(`### ${index + 1}. ${step.title}`, '', `Run on: **${step.runOn}**.`, '',
      '```text', step.command, '```', '', `Expected: ${step.expected}`, '', `If not: ${step.failure}`, '');
  }
  lines.push('References: ' + route.docs.map(([label, file]) => {
    const [filename, fragment] = file.split('#');
    const relative = path.relative(path.dirname(target), path.resolve(mainRoot, filename)).replaceAll('\\', '/');
    return `[${label}](${relative}${fragment ? '#' + fragment : ''})`;
  }).join(' · '), '');
}
await writeFile(target, lines.join('\n').trimEnd() + '\n', 'utf8');
console.log(`Exported ${additionalRoutes.length} extended routes to ${target}`);
