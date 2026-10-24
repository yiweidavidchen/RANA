/** Export the three requested flat CSVs from frozen_records.json.
 * Uses the analysis runtime's artifact-tool, not RANA dependencies.
 * Usage: node export_tables.mjs --runtime-dir <directory with node_modules>
 * Refuses to overwrite existing CSVs. No XLSX or score file is produced.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const directory=path.dirname(fileURLToPath(import.meta.url));
const runtimeIndex=process.argv.indexOf('--runtime-dir');
const runtime=runtimeIndex>=0 ? path.resolve(process.argv[runtimeIndex+1]) : directory;
const require=createRequire(path.join(runtime,'package.json'));
const {Workbook}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const frozen=JSON.parse(await fs.readFile(path.join(directory,'frozen_records.json'),'utf8'));
const workbook=Workbook.create();
const specifications=[
  ['T4L','t4l_stability_master','t4l_stability_master.csv'],
  ['Presentations','observation_presentations','observation_presentations.csv'],
  ['Ferritin','ferritin_conjugation_comparison','ferritin_conjugation_comparison.csv'],
];
const prepared=[];
for(const [sheetName,key,filename] of specifications){
  const target=path.join(directory,filename);
  try{await fs.access(target);throw new Error('Refusing to overwrite '+target);}catch(error){if(error.code!=='ENOENT')throw error;}
  const records=frozen[key];
  const headers=Object.keys(records[0]);
  if(!records.every(r=>JSON.stringify(Object.keys(r))===JSON.stringify(headers)))throw new Error('Schema varies: '+key);
  const matrix=[headers,...records.map(r=>headers.map(h=>r[h]??null))];
  if(!matrix.flat().every(v=>v===null||['string','number','boolean'].includes(typeof v)))throw new Error('Non-flat record');
  const sheet=workbook.worksheets.add(sheetName);
  sheet.getRangeByIndexes(0,0,matrix.length,headers.length).values=matrix;
  prepared.push({sheet,matrix,filename,records});
}
workbook.recalculate();
const quote=value=>{
  if(value===null||value===undefined)return '';
  const text=String(value);
  return /[",\r\n]/.test(text) ? '"'+text.replaceAll('"','""')+'"' : text;
};
for(const {sheet,matrix,filename,records} of prepared){
  const checked=sheet.getRangeByIndexes(0,0,matrix.length,matrix[0].length).values;
  for(let i=0;i<matrix.length;i++)for(let j=0;j<matrix[i].length;j++){
    if((checked[i][j]??null)!==matrix[i][j])throw new Error(`Round-trip mismatch: ${filename} ${i},${j}`);
  }
  const csv=checked.map(row=>row.map(quote).join(',')).join('\n')+'\n';
  await fs.writeFile(path.join(directory,filename),csv,{encoding:'utf8',flag:'wx'});
  console.log(JSON.stringify({file:filename,rows:records.length,columns:matrix[0].length,typedValuesRoundTrip:true}));
}
console.log((await workbook.inspect({kind:'table',range:'T4L!J1:R7',include:'values',tableMaxRows:7,tableMaxCols:9,maxChars:2500})).ndjson);
