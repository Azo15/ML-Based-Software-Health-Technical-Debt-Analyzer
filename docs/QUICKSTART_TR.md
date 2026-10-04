# CodeScope — Windows'ta başlatma

Gereksinimler: Python 3.12 ve Git. Komutları proje ana klasöründe PowerShell ile
çalıştırın. Bu sürüm Windows ve Python 3.12 üzerinde doğrulanmıştır.

## İlk kurulum

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip check
```

`py` bulunamıyorsa Python 3.12 kurulumu gerekir. Python 3.12 çalıştırıcısının tam
yolunu biliyorsanız ilk komutta `py -3.12` yerine o yolu kullanabilirsiniz.

## Her kullanımda

```powershell
.\start.cmd
```

Tarayıcıda `http://127.0.0.1:8765/` adresini açın. Terminal açık kalmalıdır;
kapatmak için Ctrl+C kullanın. Aynı veritabanıyla ikinci bir uygulama açmayın.
Uygulama kapanmışsa adres açılmaz; yeniden `start.cmd` çalıştırın.

1. **Proje klasörü** alanına Python dosyaları içeren yerel Git deposunun tam
   yolunu yapıştırın. Bir alt klasör yerine deponun ana klasörünü kullanın.
2. **Analizi başlat** düğmesine basın. Analiz aşaması ekranda güncellenir.
3. Dosya adına göre arama yapın ve bir dosyaya tıklayarak bakım önerilerini açın.
4. JSON veya CSV raporunu indirin. Soldaki geçmişten eski sonuçları açabilirsiniz.

Risk hesaplanamaması küçük veri kümelerinde beklenen bir durumdur. Bakım bulguları
yine görüntülenir. Risk skoru hata olasılığı değildir. Kaynak kod değişikliği veya
otomatik düzeltme yapılmaz. Yerel yollar ve raporlar uygulama veritabanında saklanır.

Port doluysa başka bir port seçin: `.\start.cmd --port 8766` ve tarayıcıda o
portu açın. Başka bir örnek hâlâ çalışıyorsa aynı veritabanı kilitlidir; yalnızca
port değiştirmek yeterli değildir. Ayrı bir deneme örneği için
`.\start.cmd --port 8766 --database reports\preview.sqlite3` kullanabilirsiniz.
Bu örneğin analiz geçmişi ayrıdır. Normal kapanış mevcut işleri bekler; zorla kapatılan işler yeniden
açılışta kesintiye uğramış olarak görünür. Uzun geçmişlerde analiz zaman alabilir.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

Bu sürüm yerel, tek kullanıcılı Python MVP'sidir. Genel internete açılmak üzere
tasarlanmamıştır. GitHub URL içe aktarma, çoklu dil ve otomatik düzeltme kapsamda
değildir. Bilimsel model doğrulaması MVP kullanılabilirliğinden ayrı devam eder.
