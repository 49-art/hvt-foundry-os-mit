/* Shop app — reads content.json and shows the shop. No frameworks, works offline. */
"use strict";
const K = ["hours","open_now","closed_now","find_us","open_map","call","whatsapp","products","order_wa","pay","add","your_order","install","offline","closed","price_note","send","clear","hello","items"];
const T = {
 en:["Opening hours","Open now","Closed now","Find us","Open map","Call","WhatsApp","Our products","Order on WhatsApp","Pay now","Add","Your order","Add this app to your phone","You're offline – showing saved info","Closed","Prices may change – please ask in the shop.","Send order","Clear","Hello, I'd like to order:","items"],
 ro:["Program","Deschis acum","Închis acum","Unde ne găsiți","Deschide harta","Sună","WhatsApp","Produsele noastre","Comandă pe WhatsApp","Plătește acum","Adaugă","Comanda ta","Adaugă aplicația pe telefon","Ești offline – vezi informațiile salvate","Închis","Prețurile se pot schimba – întrebați în magazin.","Trimite comanda","Golește","Bună ziua, aș dori să comand:","produse"],
 pl:["Godziny otwarcia","Otwarte teraz","Teraz zamknięte","Jak nas znaleźć","Otwórz mapę","Zadzwoń","WhatsApp","Nasze produkty","Zamów przez WhatsApp","Zapłać teraz","Dodaj","Twoje zamówienie","Dodaj aplikację do telefonu","Jesteś offline – pokazujemy zapisane informacje","Zamknięte","Ceny mogą się zmienić – zapytaj w sklepie.","Wyślij zamówienie","Wyczyść","Dzień dobry, chciałbym zamówić:","szt."],
 ar:["ساعات العمل","مفتوح الآن","مغلق الآن","موقعنا","افتح الخريطة","اتصل","واتساب","منتجاتنا","اطلب عبر واتساب","ادفع الآن","أضف","طلبك","أضف التطبيق إلى هاتفك","أنت غير متصل – نعرض المعلومات المحفوظة","مغلق","الأسعار قابلة للتغيير – اسأل في المحل.","أرسل الطلب","امسح","مرحباً، أود أن أطلب:","قطعة"],
 tr:["Çalışma saatleri","Şimdi açık","Şimdi kapalı","Bizi bulun","Haritada aç","Ara","WhatsApp","Ürünlerimiz","WhatsApp ile sipariş ver","Şimdi öde","Ekle","Siparişiniz","Uygulamayı telefonunuza ekleyin","Çevrimdışısınız – kayıtlı bilgiler gösteriliyor","Kapalı","Fiyatlar değişebilir – lütfen mağazaya sorun.","Siparişi gönder","Temizle","Merhaba, sipariş vermek istiyorum:","adet"],
 bg:["Работно време","Отворено сега","Затворено сега","Как да ни намерите","Отвори картата","Обади се","WhatsApp","Нашите продукти","Поръчай в WhatsApp","Плати сега","Добави","Вашата поръчка","Добавете приложението към телефона си","Нямате връзка – показваме запазената информация","Затворено","Цените може да се променят – попитайте в магазина.","Изпрати поръчката","Изчисти","Здравейте, бих искал да поръчам:","бр."],
 uk:["Години роботи","Зараз відчинено","Зараз зачинено","Як нас знайти","Відкрити карту","Подзвонити","WhatsApp","Наші товари","Замовити у WhatsApp","Оплатити","Додати","Ваше замовлення","Додайте застосунок на телефон","Ви офлайн – показуємо збережену інформацію","Зачинено","Ціни можуть змінюватися – запитайте в магазині.","Надіслати замовлення","Очистити","Добрий день, я хочу замовити:","шт."],
 lt:["Darbo laikas","Dabar atidaryta","Dabar uždaryta","Kaip mus rasti","Atidaryti žemėlapį","Skambinti","WhatsApp","Mūsų prekės","Užsakyti per WhatsApp","Mokėti dabar","Pridėti","Jūsų užsakymas","Pridėkite programėlę į telefoną","Esate neprisijungę – rodoma išsaugota informacija","Uždaryta","Kainos gali keistis – klauskite parduotuvėje.","Siųsti užsakymą","Išvalyti","Laba diena, norėčiau užsisakyti:","vnt."],
 el:["Ωράριο","Ανοιχτά τώρα","Κλειστά τώρα","Πού θα μας βρείτε","Άνοιγμα χάρτη","Κλήση","WhatsApp","Τα προϊόντα μας","Παραγγελία στο WhatsApp","Πληρωμή τώρα","Προσθήκη","Η παραγγελία σας","Προσθέστε την εφαρμογή στο κινητό σας","Είστε εκτός σύνδεσης – εμφανίζονται αποθηκευμένες πληροφορίες","Κλειστά","Οι τιμές μπορεί να αλλάξουν – ρωτήστε στο κατάστημα.","Αποστολή παραγγελίας","Καθαρισμός","Γεια σας, θα ήθελα να παραγγείλω:","τεμ."],
 pt:["Horário","Aberto agora","Fechado agora","Onde estamos","Abrir mapa","Ligar","WhatsApp","Os nossos produtos","Encomendar pelo WhatsApp","Pagar agora","Adicionar","O seu pedido","Adicione a app ao seu telemóvel","Está offline – a mostrar a informação guardada","Fechado","Os preços podem mudar – pergunte na loja.","Enviar pedido","Limpar","Olá, gostaria de encomendar:","itens"],
 zh:["营业时间","正在营业","已打烊","店铺位置","打开地图","打电话","WhatsApp","我们的商品","通过WhatsApp下单","立即付款","添加","您的订单","将应用添加到手机","您已离线——正在显示已保存的信息","休息","价格可能变动，请到店咨询。","发送订单","清空","您好，我想订购：","件"],
 fa:["ساعات کاری","الان باز است","الان بسته است","آدرس ما","باز کردن نقشه","تماس","واتس‌اپ","محصولات ما","سفارش از طریق واتس‌اپ","پرداخت","افزودن","سفارش شما","این برنامه را به گوشی خود اضافه کنید","آفلاین هستید – اطلاعات ذخیره‌شده نمایش داده می‌شود","بسته","قیمت‌ها ممکن است تغییر کند – در فروشگاه بپرسید.","ارسال سفارش","پاک کردن","سلام، می‌خواهم سفارش بدهم:","عدد"],
 ur:["اوقاتِ کار","ابھی کھلا ہے","ابھی بند ہے","ہمارا پتہ","نقشہ کھولیں","کال کریں","واٹس ایپ","ہماری مصنوعات","واٹس ایپ پر آرڈر کریں","ابھی ادائیگی کریں","شامل کریں","آپ کا آرڈر","یہ ایپ اپنے فون میں شامل کریں","آپ آف لائن ہیں – محفوظ معلومات دکھائی جا رہی ہیں","بند","قیمتیں بدل سکتی ہیں – دکان پر پوچھیں۔","آرڈر بھیجیں","صاف کریں","السلام علیکم، میں آرڈر کرنا چاہتا ہوں:","عدد"],
 bn:["খোলার সময়","এখন খোলা","এখন বন্ধ","আমাদের ঠিকানা","মানচিত্র খুলুন","কল করুন","হোয়াটসঅ্যাপ","আমাদের পণ্য","হোয়াটসঅ্যাপে অর্ডার করুন","এখন পরিশোধ করুন","যোগ করুন","আপনার অর্ডার","অ্যাপটি ফোনে যোগ করুন","আপনি অফলাইনে আছেন – সংরক্ষিত তথ্য দেখানো হচ্ছে","বন্ধ","দাম বদলাতে পারে – দোকানে জিজ্ঞাসা করুন।","অর্ডার পাঠান","মুছুন","হ্যালো, আমি অর্ডার করতে চাই:","টি"],
 hi:["खुलने का समय","अभी खुला है","अभी बंद है","हमें कहाँ पाएँ","नक्शा खोलें","कॉल करें","व्हाट्सऐप","हमारे उत्पाद","व्हाट्सऐप पर ऑर्डर करें","अभी भुगतान करें","जोड़ें","आपका ऑर्डर","यह ऐप अपने फ़ोन में जोड़ें","आप ऑफ़लाइन हैं – सहेजी गई जानकारी दिखाई जा रही है","बंद","कीमतें बदल सकती हैं – दुकान में पूछें।","ऑर्डर भेजें","साफ़ करें","नमस्ते, मैं ऑर्डर करना चाहता हूँ:","आइटम"],
 so:["Saacadaha furan","Hadda waa furan yahay","Hadda waa xiran yahay","Halka aan joogno","Fur khariidadda","Wac","WhatsApp","Alaabadayada","Ku dalbo WhatsApp","Hadda bixi","Ku dar","Dalabkaaga","App-kan ku dar taleefankaaga","Internet ma lihid – waxaa la muujinayaa macluumaadka la kaydiyay","Xiran","Qiimaha wuu isbeddeli karaa – dukaanka weydii.","Dir dalabka","Tirtir","Salaan, waxaan rabaa inaan dalbado:","xabbo"],
 fr:["Horaires","Ouvert maintenant","Fermé maintenant","Nous trouver","Ouvrir la carte","Appeler","WhatsApp","Nos produits","Commander sur WhatsApp","Payer maintenant","Ajouter","Votre commande","Ajoutez l'appli à votre téléphone","Vous êtes hors ligne – informations enregistrées affichées","Fermé","Les prix peuvent changer – demandez en magasin.","Envoyer la commande","Vider","Bonjour, je voudrais commander :","articles"],
};
const FALLBACK = { prs: "fa" };   // other languages without screen words use English for the buttons; the owner's own text still shows in their language
const RTL = new Set(["ar","fa","ur","ps","ckb","prs","he"]);
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let C = null, L = "en", basket = {};

function t(k) { const arr = T[L] || T[FALLBACK[L]] || T.en; return arr[K.indexOf(k)] ?? T.en[K.indexOf(k)]; }
function tx(obj) { if (!obj) return ""; if (typeof obj === "string") return obj; return obj[L] || obj[C.default_language] || Object.values(obj)[0] || ""; }
function money(p) { return p ? "£" + Number(p).toFixed(2) : ""; }
function locale() { return { zh: "zh-CN", prs: "fa-AF", kmr: "ku", ckb: "ckb" }[L] || L; }

function openState() {
  const now = new Date(), idx = (now.getDay() + 6) % 7, h = C.hours[idx];
  if (!h || h.closed) return false;
  const m = now.getHours() * 60 + now.getMinutes(), tm = s => +s.slice(0, 2) * 60 + +s.slice(3);
  return m >= tm(h.open) && m < tm(h.close);
}
function dayName(i) { const d = new Date(2024, 0, 1 + i); try { return d.toLocaleDateString(locale(), { weekday: "long" }); } catch (e) { return d.toLocaleDateString("en-GB", { weekday: "long" }); } }

function render() {
  document.documentElement.lang = L; document.documentElement.dir = RTL.has(L) ? "rtl" : "ltr";
  const s = document.documentElement.style, col = C.colours;
  s.setProperty("--p", col.primary); s.setProperty("--a", col.accent); s.setProperty("--bg", col.bg); s.setProperty("--t", col.text);
  const open = openState(), today = (new Date().getDay() + 6) % 7;
  const cats = {}; C.products.forEach(p => (cats[p.category || ""] = cats[p.category || ""] || []).push(p));
  const wa = C.whatsapp ? C.whatsapp.replace(/^0/, "44").replace(/\D/g, "") : "";
  document.getElementById("app").innerHTML = `
  ${C.demo ? `<div class="demo">DEMO SHOP – NOT A REAL BUSINESS</div>` : ""}
  <div class="offline" id="off">${esc(t("offline"))}</div>
  <header class="hero"><div class="top">${C.logo ? `<img class="logo" src="${esc(C.logo)}" alt="">` : `<div class="logo txt">${esc(C.name.slice(0, 1))}</div>`}
    <div><h1>${esc(C.name)}</h1>${tx(C.tagline) ? `<p>${esc(tx(C.tagline))}</p>` : ""}</div></div>
    <span class="status ${open ? "open" : "closed"}">${esc(open ? t("open_now") : t("closed_now"))}</span>
    ${C.languages.length > 1 ? `<div class="langs">${C.languages.map(l => `<button data-l="${l}" class="${l === L ? "on" : ""}">${esc(C.lang_names[l] || l)}</button>`).join("")}</div>` : ""}
  </header>
  ${C.announcement_on && tx(C.announcement) ? `<div class="banner">★ ${esc(tx(C.announcement))}</div>` : ""}
  <main>
    <div class="actions">${C.phone ? `<a class="btn p" href="tel:${esc(C.phone.replace(/\s/g, ""))}">📞 ${esc(t("call"))}</a>` : ""}
      ${wa ? `<a class="btn wa" href="https://wa.me/${wa}">💬 ${esc(t("whatsapp"))}</a>` : ""}
      ${C.map_url ? `<a class="btn a" href="${esc(C.map_url)}" target="_blank" rel="noopener">📍 ${esc(t("open_map"))}</a>` : ""}
      <button class="btn ghost install" id="inst">⬇ ${esc(t("install"))}</button></div>
    ${C.products.length ? `<section class="card"><h2>${esc(t("products"))}</h2>
      ${Object.entries(cats).map(([cat, ps]) => `${cat ? `<div class="cat">${esc(cat)}</div>` : ""}${ps.map(p => `
        <div class="prod ${p.in_stock ? "" : "out"}"><div class="info"><div class="nm">${esc(tx(p.name))}</div>${tx(p.description) ? `<div class="ds">${esc(tx(p.description))}</div>` : ""}
          ${p.pay_link && p.in_stock ? `<a class="btn a pay" href="${esc(p.pay_link)}" target="_blank" rel="noopener">${esc(t("pay"))}</a>` : ""}</div>
          <div class="pr">${esc(money(p.price))}${p.unit ? `<div class="ds">/${esc(p.unit)}</div>` : ""}</div>
          ${C.features.whatsapp_order && wa && p.in_stock ? `<div class="qty"><button data-m="${esc(p.id)}" aria-label="-">−</button><span id="q-${esc(p.id)}">${basket[p.id] || 0}</span><button data-p="${esc(p.id)}" aria-label="+">+</button></div>` : ""}
        </div>`).join("")}`).join("")}
      <div class="note">${esc(t("price_note"))}</div></section>` : ""}
    <section class="card"><h2>${esc(t("hours"))}</h2><table class="hours">${C.hours.map((h, i) => `<tr class="${i === today ? "today" : ""}"><td>${esc(dayName(i))}</td><td dir="ltr">${h.closed ? esc(t("closed")) : esc(h.open + " – " + h.close)}</td></tr>`).join("")}</table>
      ${tx(C.hours_note) ? `<div class="note">${esc(tx(C.hours_note))}</div>` : ""}</section>
    ${C.address ? `<section class="card"><h2>${esc(t("find_us"))}</h2><div>${esc(C.address)}${C.postcode ? ", " + esc(C.postcode) : ""}</div>
      ${C.map_url ? `<p><a class="btn ghost" href="${esc(C.map_url)}" target="_blank" rel="noopener">📍 ${esc(t("open_map"))}</a></p>` : ""}</section>` : ""}
  </main>
  <div class="basket" id="bk"><div class="sum" id="bksum"></div><button class="btn ghost" id="bkclr" style="border-color:#fff;color:#fff">${esc(t("clear"))}</button><a class="btn wa" id="bksend" target="_blank" rel="noopener">${esc(t("send"))}</a></div>
  <footer>${esc(C.made_with || "")}</footer>`;
  document.querySelectorAll("[data-l]").forEach(b => b.onclick = () => { L = b.dataset.l; localStorage.setItem("lang", L); render(); });
  document.querySelectorAll("[data-p]").forEach(b => b.onclick = () => { basket[b.dataset.p] = (basket[b.dataset.p] || 0) + 1; upd(); });
  document.querySelectorAll("[data-m]").forEach(b => b.onclick = () => { basket[b.dataset.m] = Math.max(0, (basket[b.dataset.m] || 0) - 1); upd(); });
  document.getElementById("bkclr").onclick = () => { basket = {}; render(); };
  setupInstall(); upd(); offline();
}
function upd() {
  const wa = (C.whatsapp || "").replace(/^0/, "44").replace(/\D/g, "");
  let n = 0, total = 0, lines = [];
  for (const p of C.products) { const q = basket[p.id] || 0; const el = document.getElementById("q-" + p.id); if (el) el.textContent = q;
    if (q) { n += q; total += q * (+p.price || 0); lines.push(`${q} × ${tx(p.name)}${p.price ? " (" + money(p.price) + ")" : ""}`); } }
  const bk = document.getElementById("bk"); bk.classList.toggle("show", n > 0);
  document.getElementById("bksum").textContent = `${t("your_order")}: ${n} ${t("items")}${total ? " · " + money(total) : ""}`;
  document.getElementById("bksend").href = `https://wa.me/${wa}?text=` + encodeURIComponent(`${t("hello")}\n${lines.join("\n")}${total ? "\n= " + money(total) : ""}`);
}
let deferred = null;
window.addEventListener("beforeinstallprompt", e => { e.preventDefault(); deferred = e; const b = document.getElementById("inst"); if (b) b.classList.add("show"); });
function setupInstall() { const b = document.getElementById("inst"); if (!b) return; if (deferred) b.classList.add("show");
  b.onclick = async () => { if (deferred) { deferred.prompt(); deferred = null; b.classList.remove("show"); } }; }
function offline() { const o = document.getElementById("off"); if (o) o.classList.toggle("show", !navigator.onLine); }
window.addEventListener("online", offline); window.addEventListener("offline", offline);

fetch("content.json", { cache: "no-cache" }).then(r => r.json()).then(c => {
  C = c; const saved = localStorage.getItem("lang");
  L = C.languages.includes(saved) ? saved : C.default_language; render();
}).catch(() => { document.getElementById("app").innerHTML = "<p class='loading'>Can't load the shop right now. Please try again.</p>"; });
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
