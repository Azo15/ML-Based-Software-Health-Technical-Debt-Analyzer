# 🩺 ML-Based Software Health & Technical Debt Analyzer

Modern yazılım projelerinde teknik borcu (technical debt) tespit etmek ve yönetmek, kodun uzun vadeli sürdürülebilirliği için kritik bir öneme sahiptir. **ML-Based Software Health & Technical Debt Analyzer**, Python projelerinin Git geçmişini analiz eden, karmaşıklık metriklerini çıkaran ve makine öğrenmesi algoritmaları kullanarak kodun sağlık durumunu otomatik olarak değerlendiren profesyonel bir komut satırı (CLI) aracıdır.

![CLI Output](assets/screenshot.png)

## 🌟 Özellikler

- **Git Geçmişi Madenciliği:** `PyDriller` entegrasyonu ile repodaki commit'leri tarar, hata düzeltmelerini (bug-fix) commit mesajlarındaki anahtar kelimelerden otomatik tespit eder.
- **Detaylı Metrik Çıkarımı:** `radon` ve `lizard` araçlarını kullanarak dosya bazında McCabe Cyclomatic Complexity, Halstead metrikleri (Volume, Difficulty, Effort) ve LOC (Lines of Code) değerlerini hesaplar.
- **Yapay Zeka Destekli Analiz:** Elde edilen metrikler ve hata-düzeltme etiketleri ile bir `RandomForestClassifier` modeli eğiterek, kodun gelecekte hataya ne kadar meyilli olduğunu tahmin eder.
- **Sağlık Skoru ve Teknik Borç İndeksi:** Sadece çıplak olasılıklar yerine, 0'dan 100'e kadar okunabilir bir **Health Score** (Sağlık Skoru) üretir. Bu skora göre Low/Medium/High olarak **Technical Debt Index** (Teknik Borç İndeksi) belirler.
- **Aksiyona Yönelik Öneriler:** Metrikler riskli seviyelere (Örn: Complexity > 10, LOC > 300) ulaştığında kullanıcıya doğrudan çözüm odaklı **Refactoring Önerileri** sunar.
- **Modern CLI Arayüzü:** `Typer` ve `Rich` kütüphaneleri ile renklendirilmiş, okunabilir ve profesyonel terminal çıktıları sağlar.

## 🏗 Mimari

Proje, S.O.L.I.D. ve Clean Code prensiplerine uygun, kolay genişletilebilir modüler bir yapıda tasarlanmıştır:

```text
ML-Based Software Health & Technical Debt Analyzer/
│
├── data_collector/          # Git geçmişi ve diff'leri çeken modül
│   └── git_miner.py         # PyDriller ile commit madenciliği ve 'bug-fix' etiketlemesi
│
├── feature_extractor/       # Kod karmaşıklık metriklerini hesaplayan katman
│   └── metrics_analyzer.py  # Radon ve Lizard kullanarak McCabe & Halstead hesabı
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
```

## 🚀 Kurulum

Aracı kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/KullaniciAdiniz/ML-Based-Software-Health-Technical-Debt-Analyzer.git
   cd "ML-Based Software Health & Technical Debt Analyzer"
   ```

2. **Sanal ortam oluşturun (Önerilir):**
   ```bash
   python -m venv venv
   # Windows için:
   venv\Scripts\activate
   # Linux/MacOS için:
   source venv/bin/activate
   ```

3. **Gerekli bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Kullanım

Kurulum tamamlandıktan sonra, CLI aracı üzerinden herhangi bir Python reposunu analiz etmeye başlayabilirsiniz.

**Temel Kullanım:**
Bulunduğunuz dizini veya belirli bir git reposunu analiz edin:
```bash
python -m cli.main analyze "C:\Hedef\Git\Reposu"
```

**Derinlemesine Analiz (Daha fazla commit tarama):**
Modelin daha fazla veriyle eğitilmesi için analiz edilecek maksimum commit sayısını artırın:
```bash
python -m cli.main analyze "C:\Hedef\Git\Reposu" --max-commits 200
```

**Spesifik Bir Dosyanın Analizi:**
Tüm projeyi eğitip, sadece belirli bir dosyanın teknik borç durumunu görmek için:
```bash
python -m cli.main analyze "C:\Hedef\Git\Reposu" --file "src/core.py"
```

## 🧠 Nasıl Çalışır?

1. **Phase 1 (Mining):** Hedef repoya bağlanılır. Geçmiş commitler okunur. "fix", "bug", "resolve" gibi kelimeler içeren commitler bulunur ve bu commitlerde değişen Python dosyalarının kaynak kodları bir veri seti olarak toplanır.
2. **Phase 2 (Metrics):** Toplanan her bir Python dosyası ayrıştırılır. Dosyadaki kod satırı sayısı (LOC), döngü/şartlı ifade karmaşıklığı (Cyclomatic Complexity) ve kodun anlaşılma zorluğu (Halstead Difficulty) gibi veriler matematiksel olarak hesaplanır.
3. **Phase 3 (Training):** Makine Öğrenmesi algoritması (Random Forest), bu karmaşıklık metrikleri ile dosyanın hatalı olma durumu (bug-fix) arasındaki ilişkiyi öğrenir.
4. **Phase 4 (Estimation):** Belirtilen (veya varsayılan) hedef dosya analiz edilir. Modelin hata olasılığı tahmini ve doğrudan metrik cezaları birleştirilerek nihai bir **Sağlık Skoru (0-100)** ortaya çıkarılır.

## 🤝 Katkıda Bulunma

Bu proje açık kaynaklıdır ve katkılarınızı bekliyoruz! 
- Yeni bir özellik eklemeden veya büyük bir refactoring yapmadan önce lütfen tartışmak için bir **Issue** açın.
- Pull Request gönderirken kodunuzun `PEP 8` standartlarına uyduğundan, gerekli Docstring ve Type Hinting içerdiğinden emin olun.

## 📄 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Daha fazla detay için `LICENSE` dosyasına (varsa) bakabilirsiniz.
