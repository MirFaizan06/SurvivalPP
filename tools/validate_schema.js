// usage: node validate_schema.js <schemaDir> <rootSchemaFile> <jsonFile...>
const fs=require('fs'),path=require('path');
const Ajv=require(path.join(process.env.SPP_NPM || path.join(__dirname, '..', '.ref', 'npm'), 'node_modules', 'ajv', 'dist', 'ajv.js'));
const dir=process.argv[2], root=process.argv[3], files=process.argv.slice(4);
const ajv=new Ajv({strict:false,allErrors:true,validateFormats:false});
function walk(d){for(const f of fs.readdirSync(d)){const p=path.join(d,f);if(fs.statSync(p).isDirectory())walk(p);else if(f.endsWith('.json')){try{const s=JSON.parse(fs.readFileSync(p,'utf8'));ajv.addSchema(s)}catch(e){console.log('skip',p,e.message)}}}}
// add dependent dirs (common etc.)
const base=path.join(process.env.BEDROCK_SAMPLES || path.join(__dirname, '..', '.ref', 'bedrock-samples'), 'metadata', 'json_schemas');
walk(base);
const rootSchema=JSON.parse(fs.readFileSync(path.join(dir,root),'utf8'));
let bad=0;
for(const f of files){
  let j; try{ let t=fs.readFileSync(f,'utf8'); j=JSON.parse(t);}catch(e){console.log('JSON PARSE FAIL',f,e.message);bad++;continue}
  const doc=j['minecraft:block']||j['minecraft:item']||j['minecraft:entity']||j['minecraft:spawn_rules']||j;
  const v=ajv.getSchema(rootSchema.$id);
  const ok=v(doc);
  if(!ok){const errs=(v.errors||[]).filter(e=>!(process.env.IGNORE_STATES && /\/description\/states\//.test(e.instancePath)) );
    if(errs.length){bad++;console.log('INVALID',path.basename(f));for(const e of errs.slice(0,6))console.log('   ',e.instancePath,e.message,JSON.stringify(e.params).slice(0,160));}}
}
console.log('checked',files.length,'bad',bad);
