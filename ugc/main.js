/* =========================================================
   Camila Cingu · site script. Enhancement only: the page works without it.
   ========================================================= */

/* ---------------------------------------------------------
   TRANSLATIONS
   English copy lives in index.html and is read from the page at load.
   `en` below only holds strings that JavaScript shows (no HTML equivalent).
   Photo and video descriptions are not here: they live in content/*.json (edited in Pages CMS).
   To add a language: copy the `it` block with every key, translate it, then add
   a matching <button data-lang="xx"> to .lang in index.html.
   --------------------------------------------------------- */
const I18N = {
  en: {
    'meta.desc': 'Camila Cingu, UGC creator and creative producer in Milan. Warm, honest short-form video and photos for beauty, home and pet brands, in Russian, English and Italian.',
    'card.tapHint': 'Tap again for sound',
    'about.introCaption': 'Meet Camila',
    'lb.error': "This video can't be played right now.",
    'stats.note': '{platform}, last {days} days. Updated {date}',
  },

  ru: {
    'meta.title': 'Camila Cingu · UGC-креатор в бьюти и креативный продюсер, Милан',
    'meta.desc': 'Camila Cingu, UGC-креатор и креативный продюсер в Милане. Тёплые, честные короткие видео и фото для брендов бьюти, товаров для дома и для животных на русском, английском и итальянском.',
    'card.tapHint': 'Нажмите ещё раз для звука',
    'lb.error': 'Сейчас это видео не воспроизводится.',

    'skip': 'Перейти к содержимому',
    'wordmark.label': 'Camila Cingu, наверх',
    'lang.label': 'Язык',
    'nav.menu': 'Меню',
    'nav.label': 'Основная навигация',
    'nav.portfolio': 'Портфолио',
    'nav.campaigns': 'Кампании',
    'nav.about': 'Обо мне',
    'nav.contact': 'Контакты',

    'hero.role': 'UGC-креатор в бьюти и креативный продюсер · Милан · RU · EN · IT',

    'about.title': 'Обо мне',
    'about.p1': 'Привет, я Камила, UGC-креатор в бьюти и креативный продюсер. Живу в Милане.',
    'about.p2': 'Снимаю тёплые, честные короткие видео и фото для брендов косметики, товаров для дома и для животных: дома, со свежими цветами и часто с кошкой, которая крадёт кадр.',
    'about.p3': 'Я выросла в Узбекистане и работаю на русском, английском и итальянском, поэтому одна съёмка может работать сразу на трёх рынках. Я заканчиваю магистратуру по маркетингу, поэтому пишу сценарий под хук и третью секунду, а не только под картинку.',
    'about.introCaption': 'Знакомство с Камилой',

    'why.title': 'Почему я?',
    'why.text': 'Мягкий, выстроенный кадр и живые моменты, на которых люди действительно останавливаются, от маркетолога, который понимает, что вы тестируете. Контент, похожий на совет подруги, на трёх языках.',
    'stats.label': 'Статистика Instagram',
    'stats.views': 'Просмотры',
    'stats.reach': 'Охват аккаунтов',
    'stats.interactions': 'Взаимодействия',
    'stats.followers': 'Подписчики',
    'stats.languages': 'Языки аудитории',
    'stats.note': '{platform}, последние {days} дней. Обновлено {date}',
    'stats.prev': 'Предыдущие показатели',
    'stats.next': 'Следующие показатели',

    'pf.title': 'UGC-видео',
    'pf.disclosure': 'Концепты и спек-работы созданы самостоятельно, если не указано, что это проект для клиента.',
    'cat.beauty': 'Бьюти',
    'cat.pets': 'Животные',
    'cat.home': 'Дом и цветы',
    'fmt.organic': 'Органика',
    'fmt.organicText': 'Органика с текстом',
    'fmt.testimonial': 'Рекламный отзыв',
    'fmt.voiceover': 'Реклама с закадровым голосом',
    'card.conceptFor': 'Концепт для',
    'card.clientFor': 'Проект для',

    'ph.title': 'UGC-фотография',

    'cs.title': 'Креативный продакшн',
    'cs.tag': 'Креативный продакшн',
    'cs.concept': 'Концепт',
    'cs.idea': 'Креативная идея',
    'cs.role': 'Моя роль',
    'cs.kit': 'Реквизит',
    'cs.process': 'Креативный процесс',
    'cs.dna': 'ДНК кампании',
    'cs.details': 'Детали',
    'cs.format': 'Формат',
    'cs.output': 'Итог',
    'cs.production': 'Продакшн',
    'cs.post': 'Постпродакшн',
    'role.cd': 'Креативный директор',
    'role.ad': 'Арт-дирекшн',
    'role.flower': 'Стайлинг реквизита и цветов',
    'role.photo': 'Фотография',
    'role.video': 'Видео и монтаж',
    'role.post': 'Постпродакшн',
    'pr.research': 'Исследование',
    'pr.concept': 'Концепт',
    'pr.styling': 'Стайлинг',
    'pr.production': 'Съёмка',
    'pr.editing': 'Монтаж',

    'c1.t1': 'В полном',
    'c1.t2': 'цвету',
    'c1.heroAlt': 'Пионы и зажжённая свеча на мраморной доске',
    'c1.keyAlt': 'Букет, развёрнутый на кухонном столе',
    'c1.concept': 'Свеча, которая пахнет как утро, когда приносят букет. Я построила кампанию вокруг этого первого часа: бумага, развёрнутая на кухонном столе, мокрые стебли на мраморе, пионы, раскрывающиеся на свету, и свеча, которая уже горит среди них. Кошка один раз проходит через кадр, потому что дома так и бывает.',
    'c1.k1': 'Ароматическая свеча, 190 г',
    'c1.k2': 'Двадцать пионов, половина ещё в бутонах',
    'c1.k3': 'Крафтовая флористическая бумага',
    'c1.k4': 'Мраморная доска',
    'c1.k5': 'Льняное полотенце',
    'c1.k6': 'Стеклянный кувшин, две маленькие вазы',
    'c1.k7': 'Секатор',
    'c1.k8': 'Кошка',
    'c1.p1': 'Айдентика бренда и история продукта',
    'c1.p2': 'Выстраиваю визуальное направление',
    'c1.p3': 'Цветы, реквизит и текстуры',
    'c1.p4': 'Съёмка при естественном утреннем свете',
    'c1.p5': 'Цветокоррекция и ритм',
    'c1.d1': 'Мягкий',
    'c1.d2': 'Цветочный',
    'c1.d3': 'Солнечный',
    'c1.d4': 'Игривый',
    'c1.d5': 'Настоящий',
    'c1.v1': 'Фото 4:5, видео 9:16',
    'c1.v2': '10 фото, 2 видео',
    'c1.v3': 'Самостоятельно, дома',
    'c1.v4': 'Цветокоррекция, ретушь',
    'c1.a1': 'Лепестки пиона на мраморе',
    'c1.a2': 'Пламя свечи среди стеблей',
    'c1.a3': 'Кошка проходит мимо букета',

    'c2.t1': 'Лён',
    'c2.t2': 'в полдень',
    'c2.heroAlt': 'Отглаженный воротник рубашки в послеобеденном свете',
    'c2.keyAlt': 'Половинки лимонов и флакон одеколона на обеденном столе',
    'c2.concept': 'Воскресный обед на вилле у озера Комо, увиденный через воротник рубашки, хозяин которой только что встал из-за стола. Одеколон ни разу не распыляют в кадре. Он живёт в отглаженном льне, разрезанных лимонах и тихом часе после обеда, когда дом засыпает.',
    'c2.k1': 'Белая льняная скатерть, 2,4 м',
    'c2.k2': 'Винтажная хлопковая рубашка, выглаженная вручную',
    'c2.k3': 'Шесть амальфийских лимонов, разрезанных на площадке',
    'c2.k4': 'Расписные керамические тарелки',
    'c2.k5': 'Складной плетёный стул',
    'c2.k6': 'Colonia, 100 мл',
    'c2.k7': 'Дорожный отпариватель',
    'c2.p1': 'Архив бренда и история его основания',
    'c2.p2': 'Тридцать кадров из кино, сокращённые до шести референсов',
    'c2.p3': 'Реквизит с миланских блошиных рынков',
    'c2.p4': 'Один день, только естественный свет',
    'c2.p5': 'Тёплая цветокоррекция, ретушь ткани',
    'c2.d1': 'Солнечный',
    'c2.d2': 'Отглаженный',
    'c2.d3': 'Неспешный',
    'c2.d4': 'Цитрусовый',
    'c2.d5': 'Наследие',
    'c2.v1': 'Фото 4:5, видео 9:16',
    'c2.v2': '12 фото, 3 видео',
    'c2.v3': 'Однодневная съёмка на локации',
    'c2.v4': 'Цветокоррекция, ретушь, звук',
    'c2.a1': 'Пустой плетёный стул у обеденного стола',
    'c2.a2': 'Флакон одеколона на сложенной салфетке',
    'c2.a3': 'Половинки лимона на расписной тарелке',
    'c2.ai': 'Генеративная заливка достроила небо в двух кадрах. Продукт, ткань и кожа не тронуты.',

    'ct.title': 'Давайте поработаем вместе',
    'ft.city': 'Милан',
    'ft.kit': 'Скачать медиакит (PDF)',
    'lb.close': 'Закрыть',
    'lb.prev': 'Предыдущее видео',
    'lb.next': 'Следующее видео',
  },

  it: {
    'meta.title': 'Camila Cingu · UGC creator beauty e creative producer, Milano',
    'meta.desc': 'Camila Cingu, UGC creator e creative producer a Milano. Video brevi e foto calde e sincere per brand beauty, casa e pet, in russo, inglese e italiano.',
    'card.tapHint': 'Tocca di nuovo per l’audio',
    'lb.error': 'Al momento questo video non si può riprodurre.',

    'skip': 'Vai al contenuto',
    'wordmark.label': 'Camila Cingu, torna su',
    'lang.label': 'Lingua',
    'nav.menu': 'Menu',
    'nav.label': 'Navigazione principale',
    'nav.portfolio': 'Portfolio',
    'nav.campaigns': 'Campagne',
    'nav.about': 'Chi sono',
    'nav.contact': 'Contatti',

    'hero.role': 'UGC creator beauty e creative producer · Milano · RU · EN · IT',

    'about.title': 'Chi sono',
    'about.p1': 'Ciao, sono Camila, UGC creator beauty e creative producer. Vivo a Milano.',
    'about.p2': 'Creo video brevi e foto calde e sincere per brand beauty, casa e pet: girati a casa, con fiori freschi e spesso con la mia gatta che ruba la scena.',
    'about.p3': 'Sono cresciuta in Uzbekistan e lavoro in russo, inglese e italiano, così uno shooting può funzionare su tre mercati. Sto finendo un master in marketing: per questo scrivo pensando all’hook e al terzo secondo, non solo all’estetica.',
    'about.introCaption': 'Ecco Camila',

    'why.title': 'Perché io?',
    'why.text': 'Uno sguardo morbido e curato e momenti di vita vera su cui le persone si fermano davvero, da una marketer che sa cosa state testando. Contenuti che sembrano il consiglio di un’amica, in tre lingue.',
    'stats.label': 'Statistiche Instagram',
    'stats.views': 'Visualizzazioni',
    'stats.reach': 'Account raggiunti',
    'stats.interactions': 'Interazioni',
    'stats.followers': 'Follower',
    'stats.languages': 'Lingue del pubblico',
    'stats.note': '{platform}, ultimi {days} giorni. Aggiornato il {date}',
    'stats.prev': 'Statistiche precedenti',
    'stats.next': 'Statistiche successive',

    'pf.title': 'Video UGC',
    'pf.disclosure': 'Concept e lavori spec realizzati in autonomia, salvo dove indicato come progetto per un cliente.',
    'cat.beauty': 'Beauty',
    'cat.pets': 'Pet',
    'cat.home': 'Casa e fiori',
    'fmt.organic': 'Organico',
    'fmt.organicText': 'Organico con testo',
    'fmt.testimonial': 'Ad testimonial',
    'fmt.voiceover': 'Ad con voiceover',
    'card.conceptFor': 'Concept per',
    'card.clientFor': 'Progetto per',

    'ph.title': 'Fotografia UGC',

    'cs.title': 'Produzione creativa',
    'cs.tag': 'Produzione creativa',
    'cs.concept': 'Concept',
    'cs.idea': 'Idea creativa',
    'cs.role': 'Il mio ruolo',
    'cs.kit': 'Kit di scena',
    'cs.process': 'Processo creativo',
    'cs.dna': 'DNA della campagna',
    'cs.details': 'Dettagli',
    'cs.format': 'Formato',
    'cs.output': 'Output',
    'cs.production': 'Produzione',
    'cs.post': 'Post-produzione',
    'role.cd': 'Direzione creativa',
    'role.ad': 'Art direction',
    'role.flower': 'Styling di oggetti e fiori',
    'role.photo': 'Fotografia',
    'role.video': 'Video e montaggio',
    'role.post': 'Post-produzione',
    'pr.research': 'Ricerca',
    'pr.concept': 'Concept',
    'pr.styling': 'Styling',
    'pr.production': 'Shooting',
    'pr.editing': 'Montaggio',

    'c1.t1': 'In piena',
    'c1.t2': 'fioritura',
    'c1.heroAlt': 'Peonie e una candela accesa su un piano di marmo',
    'c1.keyAlt': 'Un bouquet appena scartato sul tavolo della cucina',
    'c1.concept': 'Una candela che profuma come la mattina in cui arriva un bouquet. Ho costruito la campagna intorno a quella prima ora: la carta aperta sul tavolo della cucina, gli steli bagnati sul marmo, le peonie che si aprono alla luce e la candela già accesa tra loro. La gatta attraversa il set una volta, perché a casa succede davvero.',
    'c1.k1': 'Candela profumata, 190 g',
    'c1.k2': 'Venti peonie, metà ancora in boccio',
    'c1.k3': 'Carta kraft da fiorista',
    'c1.k4': 'Piano di marmo',
    'c1.k5': 'Strofinaccio di lino',
    'c1.k6': 'Una caraffa di vetro, due vasetti',
    'c1.k7': 'Cesoie da fiori',
    'c1.k8': 'La gatta',
    'c1.p1': 'Identità del brand e storia del prodotto',
    'c1.p2': 'Definire la direzione visiva',
    'c1.p3': 'Fiori, oggetti e texture',
    'c1.p4': 'Shooting con luce naturale del mattino',
    'c1.p5': 'Color grading e ritmo',
    'c1.d1': 'Morbido',
    'c1.d2': 'Floreale',
    'c1.d3': 'Luminoso',
    'c1.d4': 'Giocoso',
    'c1.d5': 'Autentico',
    'c1.v1': 'Foto 4:5, video 9:16',
    'c1.v2': '10 foto, 2 video',
    'c1.v3': 'In autonomia, a casa',
    'c1.v4': 'Color grading, ritocco',
    'c1.a1': 'Petali di peonia sul marmo',
    'c1.a2': 'La fiamma della candela tra gli steli',
    'c1.a3': 'La gatta passa accanto al bouquet',

    'c2.t1': 'Lino',
    'c2.t2': 'a mezzogiorno',
    'c2.heroAlt': 'Il colletto stirato di una camicia nella luce del pomeriggio',
    'c2.keyAlt': 'Mezzi limoni e un flacone di colonia sulla tavola da pranzo',
    'c2.concept': 'Un pranzo della domenica in una villa sul lago di Como, visto attraverso il colletto di una camicia appena alzata da tavola. La colonia non viene mai spruzzata in camera. Vive nel lino stirato, nei limoni tagliati e nell’ora tranquilla dopo pranzo, quando la casa si addormenta.',
    'c2.k1': 'Tovaglia di lino bianco, 2,4 m',
    'c2.k2': 'Camicia vintage di cotone, stirata a mano',
    'c2.k3': 'Sei limoni della Costiera, tagliati sul set',
    'c2.k4': 'Piatti in ceramica dipinta',
    'c2.k5': 'Sedia pieghevole in vimini',
    'c2.k6': 'Colonia, 100 ml',
    'c2.k7': 'Vaporizzatore da viaggio',
    'c2.p1': 'Archivio del brand e storia della fondazione',
    'c2.p2': 'Trenta fotogrammi di film, ridotti a sei riferimenti',
    'c2.p3': 'Oggetti dai mercatini dell’usato di Milano',
    'c2.p4': 'Un giorno, solo luce naturale',
    'c2.p5': 'Color grading caldo, ritocco dei tessuti',
    'c2.d1': 'Luminoso',
    'c2.d2': 'Stirato',
    'c2.d3': 'Lento',
    'c2.d4': 'Agrumato',
    'c2.d5': 'Heritage',
    'c2.v1': 'Foto 4:5, video 9:16',
    'c2.v2': '12 foto, 3 video',
    'c2.v3': 'Un giorno di shooting in location',
    'c2.v4': 'Color grading, ritocco, audio',
    'c2.a1': 'Una sedia di vimini vuota accanto alla tavola',
    'c2.a2': 'Il flacone di colonia su un tovagliolo piegato',
    'c2.a3': 'Mezzi limoni su un piatto dipinto',
    'c2.ai': 'Il riempimento generativo ha esteso il cielo in due inquadrature. Prodotto, tessuto e pelle non sono stati toccati.',

    'ct.title': 'Lavoriamo insieme',
    'ft.city': 'Milano',
    'ft.kit': 'Scarica il media kit (PDF)',
    'lb.close': 'Chiudi',
    'lb.prev': 'Video precedente',
    'lb.next': 'Video successivo',
  },
};

// Russian and Italian for the media Camila edits in Pages CMS. build.py writes them into the page.
const cmsI18n = document.getElementById('cms-i18n');
if (cmsI18n) {
  const extra = JSON.parse(cmsI18n.textContent);
  for (const l of Object.keys(extra)) Object.assign(I18N[l], extra[l]);
}

const LANGS = Object.keys(I18N);
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

/* ---------- i18n ---------- */
let lang = 'en';

function t(key) {
  return I18N[lang][key] ?? I18N.en[key] ?? key;
}

function parseAttrMap(el) {
  return el.dataset.i18nAttr.split(';').map(pair => pair.split(':').map(s => s.trim()));
}

function captureEnglish() {
  const en = I18N.en;
  en['meta.title'] = document.title;
  for (const el of $$('[data-i18n]')) {
    if (!(el.dataset.i18n in en)) en[el.dataset.i18n] = el.innerHTML.trim();
  }
  for (const el of $$('[data-i18n-attr]')) {
    for (const [attr, key] of parseAttrMap(el)) {
      if (!(key in en)) en[key] = el.getAttribute(attr) ?? '';
    }
  }
}

function setLang(next) {
  lang = LANGS.includes(next) ? next : 'en';
  document.documentElement.lang = lang;
  document.title = t('meta.title');
  $('meta[name="description"]').setAttribute('content', t('meta.desc'));
  for (const el of $$('[data-i18n]')) el.innerHTML = t(el.dataset.i18n);
  for (const el of $$('[data-i18n-attr]')) {
    for (const [attr, key] of parseAttrMap(el)) el.setAttribute(attr, t(key));
  }
  for (const btn of $$('.lang [data-lang]')) btn.setAttribute('aria-pressed', String(btn.dataset.lang === lang));
  renderStats();
  try { localStorage.setItem('lang', lang); } catch (e) { /* storage blocked: keep in-memory choice */ }
}

function initLang() {
  captureEnglish();
  let saved = null;
  try { saved = localStorage.getItem('lang'); } catch (e) { /* ignore */ }
  for (const btn of $$('.lang [data-lang]')) btn.addEventListener('click', () => setLang(btn.dataset.lang));
  setLang(saved || 'en');
}

/* ---------- stats slider (numbers from stats.json) ---------- */
let stats = null;

function formatCount(n) {
  const opts = n >= 10000 ? { notation: 'compact', maximumFractionDigits: 0 } : {};
  return new Intl.NumberFormat(lang, opts).format(n);
}

function renderStats() {
  if (!stats) return;
  for (const el of $$('[data-stat]')) {
    const key = el.dataset.stat;
    el.textContent = key === 'languages'
      ? stats.languages.map(l => l.code.toUpperCase() + ' ' + Math.round(l.percent) + '%').join(' · ')
      : formatCount(stats[key]);
  }
  const date = new Intl.DateTimeFormat(lang, { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(stats.updated));
  $('[data-stats-note]').textContent = t('stats.note')
    .replace('{platform}', stats.platform).replace('{days}', stats.periodDays).replace('{date}', date);
}

async function initStats() {
  const box = $('.stats');
  try {
    // no-cache: always check the server, so an edited stats.json shows up at once
    const res = await fetch('stats.json', { cache: 'no-cache' });
    if (!res.ok) return;
    stats = await res.json();
  } catch (e) { return; /* file missing or offline: keep the block hidden */ }
  renderStats();
  box.hidden = false;

  const track = $('.stats__track');
  const [prev, next] = $$('.stats__btn');
  const update = () => {
    prev.disabled = track.scrollLeft <= 1;
    next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 1;
  };
  for (const btn of [prev, next]) {
    btn.addEventListener('click', () => track.scrollBy({
      left: Number(btn.dataset.dir) * $('.stat').offsetWidth,
      behavior: reducedMotion ? 'auto' : 'smooth',
    }));
  }
  track.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
}

/* ---------- mobile menu ---------- */
function initMenu() {
  const btn = $('.menu-btn');
  const nav = $('#site-nav');
  const set = open => {
    btn.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  };
  btn.addEventListener('click', () => set(btn.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', e => { if (e.target.closest('a')) set(false); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) { set(false); btn.focus(); }
  });
}

/* ---------- video cards: hover / tap previews ---------- */
const videoLinks = $$('.js-video');
const cards = $$('.card');

// The preview <video> is created when a card nears the viewport, with preload="none":
// no video bytes load until the visitor hovers or taps.
function attachVideo(card) {
  if ($('video', card)) return;
  const link = $('.card__media', card);
  const video = document.createElement('video');
  video.muted = true;
  video.loop = true;
  video.playsInline = true;
  video.preload = 'none';
  video.setAttribute('aria-hidden', 'true');
  video.src = link.getAttribute('href');
  link.append(video);
}

function startPreview(card) {
  attachVideo(card);
  card.classList.add('is-playing');
  $('video', card).play().catch(() => card.classList.remove('is-playing'));
}

function stopPreview(card) {
  card.classList.remove('is-playing', 'is-armed');
  $('.card__hint', card)?.remove();
  $('video', card)?.pause();
}

function initVideos() {
  const io = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) { attachVideo(entry.target); io.unobserve(entry.target); }
    }
  }, { rootMargin: '400px 0px' });
  cards.forEach(card => io.observe(card));

  for (const link of videoLinks) {
    const card = link.closest('.card');

    if (card && canHover && !reducedMotion) {
      link.addEventListener('mouseenter', () => startPreview(card));
      link.addEventListener('mouseleave', () => stopPreview(card));
    }

    link.addEventListener('click', e => {
      e.preventDefault();
      // Touch on a card: first tap plays a muted preview, second tap opens with sound.
      const isTouch = !canHover && e.detail > 0;
      if (card && isTouch && !reducedMotion && !card.classList.contains('is-armed')) {
        cards.filter(c => c !== card).forEach(stopPreview);
        startPreview(card);
        card.classList.add('is-armed');
        const hint = document.createElement('span');
        hint.className = 'card__hint';
        hint.textContent = t('card.tapHint');
        link.append(hint);
        return;
      }
      if (card) stopPreview(card);
      openLightbox(link);
    });
  }
}

/* ---------- lightbox ---------- */
const lightbox = $('.lightbox');
const lbVideo = $('.lightbox__video');
const lbCaption = $('.lightbox__caption');
let lbLink = null;

function captionFor(link) {
  const card = link.closest('.card');
  if (card) return `${$('.card__brand', card).textContent} · ${$('.card__format', card).textContent}`;
  return t(link.dataset.captionKey);
}

function showInLightbox(link) {
  lbLink = link;
  lbVideo.src = link.getAttribute('href');
  lbVideo.poster = $('img', link).getAttribute('src');
  lbVideo.muted = false;
  lbCaption.textContent = captionFor(link);
  lbVideo.play().catch(() => { /* autoplay with sound blocked: controls stay available */ });
}

function openLightbox(link) {
  showInLightbox(link);
  lightbox.showModal();
}

function stepLightbox(dir) {
  const i = videoLinks.indexOf(lbLink);
  showInLightbox(videoLinks[(i + dir + videoLinks.length) % videoLinks.length]);
}

function initLightbox() {
  $('.lb-close').addEventListener('click', () => lightbox.close());
  $('.lb-prev').addEventListener('click', () => stepLightbox(-1));
  $('.lb-next').addEventListener('click', () => stepLightbox(1));
  lightbox.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); stepLightbox(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); stepLightbox(1); }
  });
  // Click on the dark backdrop (outside the video and buttons) closes.
  lightbox.addEventListener('click', e => {
    if (e.target === lightbox || e.target.classList.contains('lightbox__frame')) lightbox.close();
  });
  lightbox.addEventListener('close', () => {
    lbVideo.pause();
    lbVideo.removeAttribute('src');
    lbVideo.load();
    lbLink?.focus();
  });
  lbVideo.addEventListener('error', () => { if (lbVideo.getAttribute('src')) lbCaption.textContent = t('lb.error'); });
}

/* ---------- scroll reveals ---------- */
function initReveal() {
  const items = $$('.reveal');
  if (reducedMotion || !('IntersectionObserver' in window)) { items.forEach(el => el.classList.add('is-in')); return; }
  const io = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) { entry.target.classList.add('is-in'); io.unobserve(entry.target); }
    }
  }, { rootMargin: '0px 0px -10% 0px' });
  items.forEach(el => io.observe(el));
}

/* ---------- boot ---------- */
initLang();
initMenu();
initVideos();
initLightbox();
initReveal();
initStats();
$('[data-year]').textContent = new Date().getFullYear();
