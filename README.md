# 🩺 ML-Based Software Health & Technical Debt Analyzer 

Modern yazılım projelerinde teknik borcu (technical debt) tespit etmek ve yönetmek, kodun uzun vadeli sürdürülebilirliği için kritik bir öneme sahiptir. **ML-Based Software Health & Technical Debt Analyzer**, Python projelerinin Git geçmişini analiz eden, karmaşıklık metriklerini çıkaran ve makine öğrenmesi algoritmaları kullanarak kodun sağlık durumunu otomatik olarak değerlendiren profesyonel bir komut satırı (CLI) aracıdır.

![CLI Output](https://github.com/user-attachments/assets/911260f0-07f1-4f93-b3f3-338c646e7ac9)

## 🌟 Özellikler

- **Git Geçmişi Madenciliği:** PyDriller entegrasyonu ile repodaki commit'leri tarar, hata düzeltmelerini (bug-fix) commit mesajlarındaki anahtar kelimelerden otomatik tespit eder.
- **Detaylı Metrik Çıkarımı:** radon ve lizard araçlarını kullanarak dosya bazında McCabe Cyclomatic Complexity, Halstead metrikleri (Volume, Difficulty, Effort) ve LOC (Lines of Code) değerlerini hesaplar.
- **Zaman sıralı risk analizi:** Random Forest, yalnızca sonraki commit'lerde hata düzeltme adayı görülen eski dosya sürümlerinden öğrenir. Eğitim daha eski, değerlendirme daha yeni commit'lerde yapılır.
- **Ayrı bakım bulguları:** Karmaşıklık, dosya boyutu ve Halstead eşikleri açık kurallarla raporlanır. Risk sıralama skoru, kalibre edilmiş hata olasılığı veya teknik borç süresi değildir.
- **Aksiyona Yönelik Öneriler:** Metrikler riskli seviyelere (Örn: Complexity > 10, LOC > 300) ulaştığında kullanıcıya doğrudan çözüm odaklı Refactoring Önerileri sunar.
- **Modern CLI Arayüzü:** Typer ve Rich kütüphaneleri ile renklendirilmiş, okunabilir ve profesyonel terminal çıktıları sağlar.

## 🏗 Mimari

Proje, S.O.L.I.D. ve Clean Code prensiplerine uygun, kolay genişletilebilir modüler bir yapıda tasarlanmıştır:

ML-Based Software Health & Technical Debt Analyzer/
│
├── data_collector/          # Git geçmişi ve diff'leri çeken modül
│   └── git_miner.py         # PyDriller ile commit madenciliği ve 'bug-fix' etiketlemesi
│
├── feature_extractor/       # Kod karmaşıklık metriklerini hesaplayan katman
│   └── metrics_analyzer.py # Radon ve Lizard kullanarak McCabe & Halstead hesabı
│
├── model/                   # ML eğitim, tahmin ve metrik hesaplama süreçleri
│   └── debt_estimator.py    # Zaman sıralı risk modeli ve ayrı bakım bulguları
│
├── cli/                     # Kullanıcının projeyi çalıştıracağı arayüz
│   └── main.py              # Typer tabanlı, modern komut satırı uygulaması
│
├── utils/                   # Ortak yardımcı araçlar
│   └── logger.py            # Rich entegrasyonlu loglama mekanizması
│
└── requirements.txt         # Proje bağımlılıkları

## 🚀 Kurulum

Python 3.12 veya üzeri gereklidir. Tekrarlanabilir kurulum için bu sürümde test edilen bağımlılıklar `requirements.lock` içinde sabitlenmiştir. `venv` klasörü Git tarafından takip edilmez; her makinede yeniden oluşturulur.

Aracı kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1. Depoyu klonlayın:
   git clone https://github.com/Azo15/ML-Based-Software-Health-Technical-Debt-Analyzer.git
   cd "ML-Based Software Health & Technical Debt Analyzer"

2. Sanal ortam oluşturun (Önerilir):
   python -m venv venv
   # Windows için:
   venv\Scripts\activate
   # Linux/MacOS için:
   source venv/bin/activate

3. Gerekli bağımlılıkları yükleyin:
   pip install -r requirements.lock

## 💻 Kullanım

Kurulum tamamlandıktan sonra, CLI aracı üzerinden herhangi bir Python reposunu analiz etmeye başlayabilirsiniz.

Temel Kullanım:
python -m cli.main analyze "C:\Hedef\Git\Reposu"

Derinlemesine Analiz (Daha fazla commit tarama):
python -m cli.main analyze "C:\Hedef\Git\Reposu" --max-commits 200

Spesifik Bir Dosyanın Analizi:
python -m cli.main analyze "C:\Hedef\Git\Reposu" --file "src/core.py"

## 🧠 Nasıl Çalışır?

1. Phase 1 (Mining): En yeni commit'lerden başlanır. Değişen Python dosyaları, yolları ve düzeltme öncesi/sonrası sürümleri toplanır.
2. Phase 2 (Metrics): Toplanan her bir Python dosyası ayrıştırılır. Dosyadaki kod satırı sayısı (LOC), döngü/şartlı ifade karmaşıklığı (Cyclomatic Complexity) ve kodun anlaşılma zorluğu (Halstead Difficulty) gibi veriler matematiksel olarak hesaplanır.
3. Phase 3 (Training): Bir dosya sürümü, yalnızca daha sonraki gözlem penceresinde aynı dosyaya ait düzeltme adayı varsa pozitif etiketlenir. Yeterli ve çeşitli veri yoksa model eğitilmez.
4. Phase 4 (Estimation): Depodaki mevcut Python dosyaları incelenir. Model uygunsa göreli risk sırası; ayrıca kural temelli bakım bulguları gösterilir. Sayısal hata olasılığı veya birleşik sağlık puanı üretilmez.

Commit mesajından bulunan düzeltme etiketleri kesin hata kanıtı değildir. Model skoru kalibre edilmemiş bir sıralama sinyalidir. Proje planı ve kabul koşulları için `docs/IMPLEMENTATION_PLAN.md` dosyasına bakın.

## 🤝 Katkıda Bulunma

Bu proje açık kaynaklıdır ve katkılarınızı bekliyoruz! 
- Yeni bir özellik eklemeden veya büyük bir refactoring yapmadan önce lütfen tartışmak için bir Issue açın.
- Pull Request gönderirken kodunuzun PEP 8 standartlarına uyduğundan, gerekli Docstring ve Type Hinting içerdiğinden emin olun.

---

# 🩺 ML-Based Software Health & Technical Debt Analyzer (English)

Identifying and managing technical debt in modern software projects is critical for long-term code maintainability. **ML-Based Software Health & Technical Debt Analyzer** is a professional Command Line Interface (CLI) tool that mines Git history of Python repositories, extracts complexity metrics, and leverages machine learning models to automatically assess code health.

## 🌟 Features

- **Git History Mining:** Integrated with PyDriller to scan repository commits and automatically detect bug-fixes based on commit message keywords.
- **Detailed Metric Extraction:** Uses radon and lizard to compute file-level McCabe Cyclomatic Complexity, Halstead Metrics (Volume, Difficulty, Effort), and Lines of Code (LOC).
- **Time-aware risk ranking:** Trains a Random Forest on earlier file revisions labeled by later fix-candidate commits, with a later commit holdout.
- **Separate maintainability findings:** Explicit complexity, size, and Halstead rules are reported independently of risk. The rank score is not a calibrated defect probability or remediation time estimate.
- **Actionable Refactoring Tips:** Offers targeted refactoring suggestions when complexity metrics exceed safe thresholds (e.g., Complexity > 10, LOC > 300).
- **Modern CLI Interface:** Features clean, color-coded terminal output powered by Typer and Rich.

## 🏗 Architecture

Designed following S.O.L.I.D. and Clean Code principles with a modular layout:

ML-Based Software Health & Technical Debt Analyzer/
│
├── data_collector/         # Git mining module
│   └── git_miner.py        # PyDriller integration & bug-fix tagging
│
├── feature_extractor/      # Code complexity analysis layer
│   └── metrics_analyzer.py # Radon & Lizard metric calculation
│
├── model/                  # ML training, prediction & scoring logic
│   └── debt_estimator.py   # Time holdout model and maintainability findings
│
├── cli/                    # User CLI interface
│   └── main.py             # Typer-based terminal application
│
├── utils/                  # Shared helper utilities
│   └── logger.py           # Rich-integrated logging mechanism
│
└── requirements.txt        # Project dependencies

## 🚀 Installation

Python 3.12 or newer is required. Use the tested, pinned dependency set in `requirements.lock` for reproducible installation. The local `venv` directory is not tracked by Git.

1. Clone the repository:
   git clone https://github.com/Azo15/ML-Based-Software-Health-Technical-Debt-Analyzer.git
   cd "ML-Based Software Health & Technical Debt Analyzer"

2. Create a virtual environment (Recommended):
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/MacOS:
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.lock
  
## 💻 Usage

Basic Analysis:
python -m cli.main analyze "C:\Path\To\Target\Repo"

Deep Analysis (Increase scanned commit limit):
python -m cli.main analyze "C:\Path\To\Target\Repo" --max-commits 200

Analyze Specific File:
python -m cli.main analyze "C:\Path\To\Target\Repo" --file "src/core.py"

The default command analyzes all current tracked Python files. Fix-message labels are weak candidates, and insufficient class diversity leaves the risk score unavailable. See `docs/IMPLEMENTATION_PLAN.md` for the remaining research and product phases.

## Local API / Yerel API (Faz 4.1)

Bağımlılıkları yükledikten sonra `python -m web --port 8765` ile API'yi başlatın.
`http://127.0.0.1:8765/docs` adresinde etkileşimli API belgesi bulunur.
Proje ve sonuç ekranları `http://127.0.0.1:8765/` adresindedir.
Kullanım ve önizleme sınırları: [`docs/WEB_UI.md`](docs/WEB_UI.md).
Launch the local API with `python -m web --port 8765`; interactive reference is at
`http://127.0.0.1:8765/docs`. See [`docs/LOCAL_API.md`](docs/LOCAL_API.md) for job
states, storage, request examples and restart behavior.

## Report export / Rapor dışa aktarma

Current-file filters / Mevcut dosya filtreleri:
`python -m cli.main analyze <repo> --exclude="tests/*" --exclude="examples/*"`

JSON raporu artık atlanan dosyaları, nedenlerini ve analiz durumunu içerir.
Filtreler mevcut dosya listesini etkiler; geçmiş eğitim verisini değiştirmez.
The shared analysis service, report fields and exit codes are documented in
[`docs/ANALYSIS_SERVICE.md`](docs/ANALYSIS_SERVICE.md).

Pass `--output report.json` or `--output report.csv` to `analyze`. The file must not
already exist. JSON includes the model evaluation, all file metrics, and complete
maintainability findings. CSV has one summary row per current Python file.

`analyze` komutuna `--output rapor.json` veya `--output rapor.csv` ekleyin.
Dosya önceden var olmamalıdır. JSON model değerlendirmesi, metrikler ve tüm bakım
bulgularını; CSV ise her Python dosyası için bir özet satırı içerir.

## 🤝 Contributing

Contributions are welcome! Please open an Issue to discuss proposed major changes before submitting a Pull Request.
