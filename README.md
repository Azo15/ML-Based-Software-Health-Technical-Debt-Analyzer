# 🩺 ML-Based Software Health & Technical Debt Analyzer 

Modern yazılım projelerinde teknik borcu (technical debt) tespit etmek ve yönetmek, kodun uzun vadeli sürdürülebilirliği için kritik bir öneme sahiptir. **ML-Based Software Health & Technical Debt Analyzer**, Python projelerinin Git geçmişini analiz eden, karmaşıklık metriklerini çıkaran ve makine öğrenmesi algoritmaları kullanarak kodun sağlık durumunu otomatik olarak değerlendiren profesyonel bir komut satırı (CLI) aracıdır.

![CLI Output](https://github.com/user-attachments/assets/911260f0-07f1-4f93-b3f3-338c646e7ac9)

## 🌟 Özellikler

- **Git Geçmişi Madenciliği:** PyDriller entegrasyonu ile repodaki commit'leri tarar, hata düzeltmelerini (bug-fix) commit mesajlarındaki anahtar kelimelerden otomatik tespit eder.
- **Detaylı Metrik Çıkarımı:** radon ve lizard araçlarını kullanarak dosya bazında McCabe Cyclomatic Complexity, Halstead metrikleri (Volume, Difficulty, Effort) ve LOC (Lines of Code) değerlerini hesaplar.
- **Yapay Zeka Destekli Analiz:** Elde edilen metrikler ve hata-düzeltme etiketleri ile bir RandomForestClassifier modeli eğiterek, kodun gelecekte hataya ne kadar meyilli olduğunu tahmin eder.
- **Sağlık Skoru ve Teknik Borç İndeksi:** Sadece çıplak olasılıklar yerine, 0'dan 100'e kadar okunabilir bir Health Score (Sağlık Skoru) üretir. Bu skora göre Low/Medium/High olarak Technical Debt Index (Teknik Borç İndeksi) belirler.
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
│   └── debt_estimator.py    # RandomForest modeli, Health Score & Debt Index hesaplaması
│
├── cli/                     # Kullanıcının projeyi çalıştıracağı arayüz
│   └── main.py              # Typer tabanlı, modern komut satırı uygulaması
│
├── utils/                   # Ortak yardımcı araçlar
│   └── logger.py            # Rich entegrasyonlu loglama mekanizması
│
└── requirements.txt         # Proje bağımlılıkları

## 🚀 Kurulum

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
   pip install -r requirements.txt

## 💻 Kullanım

Kurulum tamamlandıktan sonra, CLI aracı üzerinden herhangi bir Python reposunu analiz etmeye başlayabilirsiniz.

Temel Kullanım:
python -m cli.main analyze "C:\Hedef\Git\Reposu"

Derinlemesine Analiz (Daha fazla commit tarama):
python -m cli.main analyze "C:\Hedef\Git\Reposu" --max-commits 200

Spesifik Bir Dosyanın Analizi:
python -m cli.main analyze "C:\Hedef\Git\Reposu" --file "src/core.py"

## 🧠 Nasıl Çalışır?

1. Phase 1 (Mining): Hedef repoya bağlanılır. Geçmiş commitler okunur. "fix", "bug", "resolve" gibi kelimeler içeren commitler bulunur ve bu commitlerde değişen Python dosyalarının kaynak kodları bir veri seti olarak toplanır.
2. Phase 2 (Metrics): Toplanan her bir Python dosyası ayrıştırılır. Dosyadaki kod satırı sayısı (LOC), döngü/şartlı ifade karmaşıklığı (Cyclomatic Complexity) ve kodun anlaşılma zorluğu (Halstead Difficulty) gibi veriler matematiksel olarak hesaplanır.
3. Phase 3 (Training): Makine Öğrenmesi algoritması (Random Forest), bu karmaşıklık metrikleri ile dosyanın hatalı olma durumu (bug-fix) arasındaki ilişkiyi öğrenir.
4. Phase 4 (Estimation): Belirtilen (veya varsayılan) hedef dosya analiz edilir. Modelin hata olasılığı tahmini ve doğrudan metrik cezaları birleştirilerek nihai bir Sağlık Skoru (0-100) ortaya çıkarılır.

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
- **AI-Powered Analysis:** Trains a RandomForestClassifier on extracted metrics and bug-fix labels to predict code error-proneness.
- **Health Score & Technical Debt Index:** Generates an intuitive Health Score (0-100) instead of raw probabilities, categorizing code into Low, Medium, or High Technical Debt Index.
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
│   └── debt_estimator.py   # RandomForest model & Debt Index evaluation
│
├── cli/                    # User CLI interface
│   └── main.py             # Typer-based terminal application
│
├── utils/                  # Shared helper utilities
│   └── logger.py           # Rich-integrated logging mechanism
│
└── requirements.txt        # Project dependencies

## 🚀 Installation

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
   pip install -r requirements.txt
  
## 💻 Usage

Basic Analysis:
python -m cli.main analyze "C:\Path\To\Target\Repo"

Deep Analysis (Increase scanned commit limit):
python -m cli.main analyze "C:\Path\To\Target\Repo" --max-commits 200

Analyze Specific File:
python -m cli.main analyze "C:\Path\To\Target\Repo" --file "src/core.py"

## 🤝 Contributing

Contributions are welcome! Please open an Issue to discuss proposed major changes before submitting a Pull Request.
