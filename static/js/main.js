document.addEventListener('DOMContentLoaded', function() {
    const mobileBtn = document.getElementById('mobile-menu-btn');
    
    if(mobileBtn) {
        mobileBtn.addEventListener('click', () => {
            console.log("Mobil menyu bosildi");
            // Bu yerga sidebar yoki menyu ochilish kodini yozishingiz mumkin
        });
    }

    // Savatga qo'shish tugmasi effekti
    const cartButtons = document.querySelectorAll('.product-card button');
    cartButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.innerHTML = '<i class="fas fa-check"></i> Qo\'shildi';
            this.classList.replace('bg-indigo-50', 'bg-green-500');
            this.classList.replace('text-indigo-600', 'text-white');
            
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-shopping-basket"></i> Savatga';
                this.classList.replace('bg-green-500', 'bg-indigo-50');
                this.classList.replace('text-white', 'text-indigo-600');
            }, 2000);
        });
    });
});

function updateQty(delta) {
    const input = document.getElementById('qty-input');
    let currentVal = parseInt(input.value);
    let maxVal = parseInt(input.getAttribute('max'));
    
    let newVal = currentVal + delta;
    
    if (newVal >= 1 && newVal <= maxVal) {
        input.value = newVal;
    }
}