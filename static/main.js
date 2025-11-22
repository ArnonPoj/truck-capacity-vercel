function createRow(){
const container = document.getElementById('product-list');
const idx = container.children.length;
const div = document.createElement('div');
div.innerHTML = `
<strong>สินค้า ${idx+1}</strong>
width(m): <input data-key="width" value="1">
length(m): <input data-key="length" value="1">
height(m): <input data-key="height" value="0.5">
weight(kg): <input data-key="weight" value="50">
<button class="remove">ลบ</button>
<br>
`;
div.querySelector('.remove').onclick = ()=>div.remove();
container.appendChild(div);
}


document.getElementById('add').onclick = ()=>createRow();


document.getElementById('compute').onclick = async ()=>{
const rows = Array.from(document.getElementById('product-list').children);
const products = rows.map(r=>{
const inputs = Array.from(r.querySelectorAll('input'));
const obj = {};
inputs.forEach(i=> obj[i.dataset.key] = parseFloat(i.value));
return obj;
});


const res = await fetch('/api/compute', {
method: 'POST',
headers: {'Content-Type':'application/json'},
body: JSON.stringify({products})
});
const j = await res.json();
document.getElementById('result').textContent = JSON.stringify(j, null, 2);
}


// add one row on load
createRow();
