/* ==========================================================================
   Art Studio by Aastha - Interactive JS Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // 1. Navbar Scroll Effect
    const header = document.getElementById('main-header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // 2. Mobile Menu Toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navLinks = document.getElementById('navigation-menu');

    mobileMenuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        // Simple animation switch for menu icon
        mobileMenuToggle.classList.toggle('open');
    });

    // Close menu when link is clicked
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Highlight active link based on scroll section
    const sections = document.querySelectorAll('section');
    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= (sectionTop - 150)) {
                current = section.getAttribute('id');
            }
        });

        links.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').slice(1) === current) {
                link.classList.add('active');
            }
        });
    });

    // 3. Product Catalog Filter
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Toggle active class
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filterValue = btn.getAttribute('data-filter');

            productCards.forEach(card => {
                const category = card.getAttribute('data-category');
                if (filterValue === 'all' || category === filterValue) {
                    card.style.display = 'flex';
                    // Trigger tiny animation
                    card.style.opacity = '0';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transition = 'opacity 0.4s ease';
                    }, 50);
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // 4. Quick View Modal Data
    const productsData = {
        hamper1: {
            title: "Classic Happiness Hamper",
            price: "₹2,499",
            desc: "Unwrap joy with a signature gift hamper curated by Art Studio by Aastha. Housed in our bespoke Blush Pink premium box, this hamper features a hand-poured aromatic soy candle, gourmet cookies, aesthetic flower arrangement accents, and a custom handwritten calligraphy greeting card customized with your message. The box is bound together by our signature satin ribbon styling.",
            image: "assets/images/hamper_1.jpg"
        },
        hamper2: {
            title: "Celebration Delight Hamper",
            price: "₹3,199",
            desc: "Designed to bring sheer delight to any milestone celebration. This luxurious hamper features an artisan chocolate set, hand-decorated mugs, customized birthday/celebration card, organic lavender tea lights, and a vibrant pastel colored box wrap. Beautifully bound with matching double-faced satin bows.",
            image: "assets/images/hamper_2.jpg"
        },
        hamper3: {
            title: "Premium Keepsake Box",
            price: "₹4,299",
            desc: "Our most premium gift hamper designed for grand occasions like weddings, anniversaries, or high-end corporate gifting. Features luxury treats, customized lifestyle pieces, a mini vintage pressed glass flower frame, customized stationery, and full aesthetic wrapping. Fully customizable themes and palettes.",
            image: "assets/images/hamper_3.jpg"
        },
        frame1: {
            title: "Mini Floating Glass Frame",
            price: "₹999",
            desc: "A gorgeous 5\" by 7\" double-paned floating glass frame. Ideal for showcasing pressed wild flowers, retro polaroid memories, invitations, or hand-painted sketches. Bound with a delicate copper or gold finish border and a hanging chain for easy room decoration.",
            image: "assets/images/glass_frame_1.jpg"
        },
        frame2: {
            title: "Square Herbarium Glass Frame",
            price: "₹1,799",
            desc: "Our premium 10\" by 10\" square pressed flower floating frame featuring a stunning array of pressed blossoms, custom name script, or artistic calligraphy. Framed in high-quality brass alloy with a vintage gold latch mechanism. A timeless piece of home decor.",
            image: "assets/images/glass_frame_2.jpg"
        }
    };

    // Modal elements
    const modal = document.getElementById('quick-view-modal');
    const modalImg = document.getElementById('modal-product-img');
    const modalTitle = document.getElementById('modal-product-title');
    const modalPrice = document.getElementById('modal-product-price');
    const modalDesc = document.getElementById('modal-product-desc');
    const closeModal = document.getElementById('close-quickview');
    const modalOrderBtn = document.getElementById('modal-order-btn');

    // Attach quick view triggers
    const quickViewButtons = document.querySelectorAll('.quick-view-btn');
    quickViewButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const productId = btn.getAttribute('data-product');
            const data = productsData[productId];
            
            if (data) {
                modalImg.src = data.image;
                modalTitle.textContent = data.title;
                modalPrice.textContent = data.price;
                modalDesc.textContent = data.desc;
                
                // Configure modal CTA to open contact form or DM
                modalOrderBtn.onclick = (e) => {
                    e.preventDefault();
                    modal.classList.remove('active');
                    
                    // Set contact form dropdown values
                    const select = document.getElementById('order-item');
                    if (productId === 'hamper1') select.value = 'classic';
                    else if (productId === 'hamper2') select.value = 'celebration';
                    else if (productId === 'hamper3') select.value = 'keepsake';
                    else if (productId === 'frame1') select.value = 'frame-mini';
                    else if (productId === 'frame2') select.value = 'frame-square';
                    
                    // Focus contact form
                    document.getElementById('contact').scrollIntoView();
                };

                modal.classList.add('active');
            }
        });
    });

    closeModal.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    // Close modal when clicking outside content block
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });


    // 5. Interactive Hamper Customizer Logic
    const boxOptions = document.querySelectorAll('#box-options-container .option-card');
    const itemsCheckboxes = document.querySelectorAll('#goodies-options-container .item-checkbox');
    const visualBoxMock = document.getElementById('visual-box-mock');
    const receiptBoxPrice = document.getElementById('receipt-box-price');
    const receiptItemsAdded = document.getElementById('receipt-items-added');
    const receiptTotalPrice = document.getElementById('receipt-total-price');
    const placeCustomOrderBtn = document.getElementById('place-custom-order-btn');

    let selectedBox = {
        name: "Blush Pink",
        price: 350,
        colorClass: "box-color-pink"
    };
    
    let selectedItems = [];

    // Box Selection
    boxOptions.forEach(opt => {
        opt.addEventListener('click', () => {
            boxOptions.forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');

            const boxName = opt.querySelector('.option-name').textContent;
            const boxPrice = parseInt(opt.getAttribute('data-price'));
            const boxType = opt.getAttribute('data-box');
            
            selectedBox.name = boxName;
            selectedBox.price = boxPrice;
            
            // Map box to preview visualization color
            if (boxType === 'pink') selectedBox.colorClass = "box-color-pink";
            else if (boxType === 'lavender') selectedBox.colorClass = "box-color-lavender";
            else if (boxType === 'peach') selectedBox.colorClass = "box-color-peach";
            else if (boxType === 'kraft') selectedBox.colorClass = "box-color-kraft";

            // Update visual mock box color class
            visualBoxMock.className = "mock-box " + selectedBox.colorClass;
            
            updateCustomizerReceipt();
        });
    });

    // Goodies Checklist Selection
    itemsCheckboxes.forEach(itemCard => {
        const checkbox = itemCard.querySelector('input[type="checkbox"]');
        
        itemCard.addEventListener('click', (e) => {
            // Prevent toggling twice if clicked on checkbox input directly
            if (e.target !== checkbox) {
                checkbox.checked = !checkbox.checked;
            }

            itemCard.classList.toggle('checked', checkbox.checked);
            
            const itemCode = itemCard.getAttribute('data-item');
            const itemTitle = itemCard.querySelector('.item-title').textContent;
            const itemCost = parseInt(itemCard.getAttribute('data-price'));

            if (checkbox.checked) {
                // Add item to active list
                if (!selectedItems.find(i => i.code === itemCode)) {
                    selectedItems.push({ code: itemCode, title: itemTitle, price: itemCost });
                }
            } else {
                // Remove item from active list
                selectedItems = selectedItems.filter(i => i.code !== itemCode);
            }

            updateCustomizerReceipt();
        });
    });

    // Calculate sum and update receipt table
    function updateCustomizerReceipt() {
        receiptBoxPrice.textContent = `₹${selectedBox.price}`;
        
        // Populate goodies list
        receiptItemsAdded.innerHTML = "";
        let totalItemsCost = 0;

        selectedItems.forEach(item => {
            totalItemsCost += item.price;
            const itemDiv = document.createElement('div');
            itemDiv.className = "receipt-item";
            itemDiv.innerHTML = `<span>+ ${item.title}</span><span>₹${item.price}</span>`;
            receiptItemsAdded.appendChild(itemDiv);
        });

        // Compute overall total
        const grandTotal = selectedBox.price + totalItemsCost;
        receiptTotalPrice.textContent = `₹${grandTotal}`;
        
        // Scale visualization mock based on size/contents
        const scaleVal = 1 + (selectedItems.length * 0.05);
        visualBoxMock.style.transform = `rotateX(20deg) rotateY(-20deg) scale(${scaleVal})`;
    }

    // Initialize customizer elements
    updateCustomizerReceipt();

    // 6. DM Order Button compilation for Customizer
    placeCustomOrderBtn.addEventListener('click', () => {
        const itemsListStr = selectedItems.length > 0 
            ? selectedItems.map((item, idx) => `  ${idx + 1}. ${item.title} (₹${item.price})`).join('\n') 
            : "  No add-on items selected";
        
        const total = selectedBox.price + selectedItems.reduce((acc, curr) => acc + curr.price, 0);

        const customMessage = `Hi Aastha! I am interested in building a custom gift hamper from your website. Here are my selections:\n\n`
            + `📦 Box Theme: ${selectedBox.name} (₹${selectedBox.price})\n`
            + `🎁 Selected Items:\n${itemsListStr}\n\n`
            + `💰 Estimated Total: ₹${total}\n\n`
            + `Please let me know how we can proceed with styling and payment!`;

        // Direct users to copy and DM
        copyMessageToClipboard(customMessage);
    });

    // 7. Contact Form order generation logic
    const contactForm = document.getElementById('contact-order-form');
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const customerName = document.getElementById('order-name').value;
        const selectedProductId = document.getElementById('order-item').value;
        const productSelector = document.getElementById('order-item');
        const productName = productSelector.options[productSelector.selectedIndex].text;
        const notes = document.getElementById('order-notes').value;

        const orderMessage = `Hi Aastha! My name is ${customerName}.\n`
            + `I am interested in ordering/inquiring about: *${productName}*.\n\n`
            + `✏️ Customization Notes:\n"${notes}"\n\n`
            + `Please let me know the availability and payment details. Thanks!`;

        copyMessageToClipboard(orderMessage);
    });

    // Helper: Copy template text and prompt redirection alert
    function copyMessageToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert("✨ Perfect! Your order details have been custom formatted and copied to your clipboard!\n\n"
                + "We are now opening Instagram DM for @artstudioby_aastha. Simply paste (Ctrl+V) the message into the chat window to submit your order!");
            
            // Redirect to Instagram page
            window.open("https://www.instagram.com/artstudioby_aastha/", "_blank");
        }).catch(err => {
            console.error("Could not copy order string: ", err);
            alert("Your custom order text was generated:\n\n" + text + "\n\nFeel free to copy this manually and send it to Aastha on Instagram!");
        });
    }
});
