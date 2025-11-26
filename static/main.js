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

document.addEventListener('DOMContentLoaded', () => {
    // add initial row
    createRow();

    document.getElementById('add').onclick = ()=>createRow();

    document.getElementById('compute').onclick = async ()=>{
        const rows = Array.from(document.getElementById('product-list').children);
        const products = rows.map(r=>{
            const inputs = Array.from(r.querySelectorAll('input'));
            const obj = {};
            obj.name = `สินค้า ${inputs[0].value || "Unnamed"}`;
            obj.width = parseFloat(inputs[0].value || 1);
            obj.length = parseFloat(inputs[1].value || 1);
            obj.height = parseFloat(inputs[2].value || 0.5);
            obj.weight_per_unit = parseFloat(inputs[3].value || 50);
            obj.quantity = parseInt(inputs[4].value || 1, 10);
            return obj;
        });

        try {
            const res = await fetch('/api/calculate-capacity', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({products})
            });
            if(!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            const j = await res.json();
            document.getElementById('result').textContent = JSON.stringify(j, null, 2);
        } catch(e){
            document.getElementById('result').textContent = `Error: ${e.message}`;
        }
    }
});
