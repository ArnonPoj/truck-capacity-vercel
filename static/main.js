function createRow() {
    const container = document.getElementById('product-list');
    const idx = container.children.length;
    const div = document.createElement('div');
    div.className = 'item-row';
    div.innerHTML = `
        <strong>สินค้า ${idx+1}</strong>
        ชื่อ: <input data-key="name" value="สินค้า ${idx+1}">
        กว้าง (ม.): <input data-key="width" type="number" value="1" step="0.01">
        ยาว (ม.): <input data-key="length" type="number" value="1" step="0.01">
        สูง (ม.): <input data-key="height" type="number" value="0.5" step="0.01">
        น้ำหนัก/ชิ้น (กก.): <input data-key="weight_per_unit" type="number" value="50" step="0.1">
        จำนวน: <input data-key="quantity" type="number" value="1" step="1">
        <button class="remove">ลบ</button>
        <br><br>
    `;
    div.querySelector('.remove').onclick = () => div.remove();
    container.appendChild(div);
}

document.addEventListener('DOMContentLoaded', () => {
    // add first row
    createRow();

    document.getElementById('add').onclick = () => createRow();

    document.getElementById('compute').onclick = async () => {
        const rows = Array.from(document.getElementById('product-list').children);
        const products = rows.map(r => {
            const inputs = r.querySelectorAll('input');
            const obj = {};
            inputs.forEach(input => {
                const key = input.dataset.key;
                if (key === 'name') obj[key] = input.value;
                else if (key === 'quantity') obj[key] = parseInt(input.value || 1, 10);
                else obj[key] = parseFloat(input.value || 0);
            });
            return obj;
        });

        try {
            const res = await fetch('/api/calculate-capacity', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ products })
            });
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            const data = await res.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
        } catch (e) {
            document.getElementById('result').textContent = `Error: ${e.message}`;
        }
    };
});
