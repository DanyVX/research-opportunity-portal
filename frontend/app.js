'use strict';
const $ = selector => document.querySelector(selector);
const fields = ['title','description','research_area','faculty_name','department','required_skills','available_positions','application_deadline','status'];
let opportunities = [], editingId = null, busy = false;
function node(tag, text, className) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (className) el.className = className; return el; }
function notice(text, success = false) { const el = $('#notice'); el.textContent = text; el.className = success ? 'success' : ''; el.hidden = false; }
async function api(path = '', options = {}) {
  const response = await fetch('/api/opportunities' + path, { ...options, headers: {'Content-Type':'application/json'} });
  const data = await response.json().catch(() => ({error:'The server returned an unreadable response.'}));
  if (!response.ok) throw new Error([data.error, ...Object.entries(data.fields || {}).map(([k,v]) => `${k.replaceAll('_',' ')}: ${v}`)].join('\n'));
  return data;
}
function writable(item) { return Object.fromEntries(fields.map(f => [f,item[f]])); }
function render() {
  const term = $('#search').value.toLowerCase().trim(), status = $('#filter').value;
  const list = opportunities.filter(o => (!status || o.status === status) && fields.some(f => String(o[f]).toLowerCase().includes(term)));
  $('#count').textContent = `${list.length} of ${opportunities.length} opportunities`;
  $('#cards').replaceChildren();
  if (!list.length) { $('#cards').append(node('div', opportunities.length ? 'No matching opportunities. Try another search.' : 'No opportunities yet. Create the first one to get started.', 'empty')); return; }
  list.forEach(o => {
    const card = node('article', undefined, 'card'), top = node('div',undefined,'card-top');
    top.append(node('span',o.research_area,'area'),node('span',o.status,'badge' + (o.status === 'Closed' ? ' closed' : '')));
    card.append(top,node('h3',o.title),node('p',o.description.length > 150 ? o.description.slice(0,150)+'…' : o.description,'description'));
    const meta = node('div',undefined,'meta');
    meta.append(node('div',`${o.faculty_name} · ${o.department}`),node('div',`${o.available_positions} position(s) · Deadline ${o.application_deadline}`));
    card.append(meta);
    const actions = node('div',undefined,'actions');
    [['Details',() => showDetails(o.id)],['Edit',() => edit(o.id)],[o.status === 'Open' ? 'Close' : 'Reopen',() => toggle(o.id)],['Delete',() => remove(o.id)]].forEach(([label,fn])=>{
      const b=node('button',label,label==='Delete'?'danger':''); b.disabled=busy; b.addEventListener('click',fn); actions.append(b);
    });
    card.append(actions); $('#cards').append(card);
  });
}
async function load() {
  $('#refresh').disabled = true;
  try { opportunities = await api(); render(); return true; }
  catch(e) { notice(e.message); if (!opportunities.length) $('#cards').replaceChildren(node('div','Could not load opportunities. Check the server and database, then press Refresh.','empty')); return false; }
  finally { $('#refresh').disabled = false; }
}
function openEditor(item = null) {
  editingId = item ? item.id : null; $('#form').reset(); $('#form-error').hidden=true;
  $('#form-title').textContent = item ? 'Edit opportunity' : 'New opportunity';
  if (item) fields.forEach(f=>$('#form').elements[f].value=item[f]);
  $('#editor').showModal();
}
async function edit(id) { try { openEditor(await api('/'+id)); } catch(e) { notice(e.message); } }
async function showDetails(id) {
  try {
    const o=await api('/'+id), dl=node('dl');
    [['id','ID'],...fields.map(f=>[f,f.replaceAll('_',' ')])].forEach(([f,label])=>{dl.append(node('dt',label),node('dd',String(o[f])));});
    $('#detail-content').replaceChildren(node('h3',o.title),dl); $('#details').showModal();
  } catch(e) { notice(e.message); }
}
async function mutate(action, message) {
  if (busy) return; busy=true; $('#new').disabled=true; render();
  try { await action(); const loaded=await load(); if (loaded) notice(message,true); else notice(message+' Refresh failed; press Refresh to load current data.'); }
  catch(e) { notice(e.message); }
  finally { busy=false; $('#new').disabled=false; render(); }
}
async function toggle(id) {
  await mutate(async()=>{const o=await api('/'+id); await api('/'+id,{method:'PUT',body:JSON.stringify({...writable(o),status:o.status==='Open'?'Closed':'Open'})});},'Opportunity status updated.');
}
async function remove(id) {
  if (!confirm('Delete this opportunity permanently?')) return;
  await mutate(()=>api('/'+id,{method:'DELETE'}),'Opportunity deleted.');
}
$('#form').addEventListener('submit',async event=>{
  event.preventDefault(); if(busy) return;
  const payload = Object.fromEntries(fields.map(f=>[f,$('#form').elements[f].value.trim()]));
  payload.available_positions=Number(payload.available_positions);
  busy=true; $('#save').disabled=true; $('#form-error').hidden=true;
  try {
    await api(editingId===null?'':'/'+editingId,{method:editingId===null?'POST':'PUT',body:JSON.stringify(payload)});
    $('#editor').close(); const loaded=await load();
    notice(loaded?'Opportunity saved.':'Opportunity saved. Refresh failed; press Refresh to load current data.',loaded);
  } catch(e) { $('#form-error').textContent=e.message; $('#form-error').hidden=false; }
  finally {busy=false; $('#save').disabled=false; render();}
});
$('#new').addEventListener('click',()=>openEditor());
$('#search').addEventListener('input',render); $('#filter').addEventListener('change',render);
$('#refresh').addEventListener('click',()=>{$('#notice').hidden=true;load();});
document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>{if(!busy) document.getElementById(b.dataset.close).close();}));
$('#editor').addEventListener('cancel',event=>{if(busy)event.preventDefault();});
load();
