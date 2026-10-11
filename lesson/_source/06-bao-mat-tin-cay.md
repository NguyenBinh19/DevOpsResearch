# Giai đoạn 6 - Bảo mật, phục hồi và tư duy vận hành sản xuất

Bảo mật và độ tin cậy là trách nhiệm xuyên suốt khóa học; giai đoạn này đào sâu và nối các mảnh đã học thành quyết định vận hành. Mọi bài tập gây lỗi, xóa hoặc khôi phục chỉ làm trên môi trường lab với dữ liệu giả.

## Bài 1. Tư duy rủi ro và quyền tối thiểu

Đừng bắt đầu bằng danh sách công cụ bảo mật. Hãy hỏi: cần bảo vệ tài sản nào, ai có thể truy cập, đường tấn công hoặc lỗi vận hành nào khả dĩ, hậu quả là gì và có thể phát hiện/giảm ảnh hưởng ra sao? Với API ghi chú, tài sản là dữ liệu ghi chú, secret database, quyền cloud, source code và pipeline. Một token CI có quyền xóa toàn bộ tài nguyên là rủi ro lớn hơn nhiều so với token chỉ được đẩy image vào registry.

Threat modeling đơn giản có thể làm trên sơ đồ request: khoanh vùng các điểm tin cậy thay đổi, như browser -> API, API -> database, CI -> cloud. Với mỗi mũi tên, hỏi authentication, authorization, encryption và log. Authentication xác nhận ai/cái gì đang gọi; authorization xác định được phép làm gì. Mã hóa đường truyền bằng TLS bảo vệ dữ liệu trên mạng nhưng không sửa quyền sai tại database. Mỗi cơ chế xử lý một lớp rủi ro khác.

Secrets gồm mật khẩu, API token, private key và credential cloud. Không đưa chúng vào Git, image, log hoặc ảnh chụp màn hình. Dùng hệ thống quản lý secret phù hợp, cấp quyền truy cập theo workload, luân chuyển khi cần và có quy trình thu hồi. Một secret bị commit rồi xóa ở commit mới vẫn có thể tồn tại trong lịch sử; phải coi nó đã lộ và rotate. Đừng tin vào việc chỉ thêm `.gitignore` sau khi lỡ commit.

### Bài tập review rủi ro

Vẽ đường từ pull request -> CI runner -> image registry -> cluster -> database. Ghi quyền tối thiểu mỗi thành phần cần. Đánh dấu nơi secret đi qua và log nào có thể vô tình lộ nó. Chọn ba rủi ro có tác động cao nhất, một biện pháp giảm xác suất, một cách phát hiện và một cách phục hồi cho từng rủi ro.

## Bài 2. Software supply chain và bảo vệ pipeline

Ứng dụng phụ thuộc thư viện, image gốc, build tools và workflow bên thứ ba. Supply chain security quan tâm nguồn gốc và tính toàn vẹn của các đầu vào/đầu ra đó. Khóa phiên bản dependency, xem cảnh báo lỗ hổng, cập nhật có kiểm tra, dùng image từ nguồn tin cậy và giữ bản ghi build/release. Quét lỗ hổng không phải phán quyết cuối: cần đánh giá liệu mã dễ bị ảnh hưởng có được dùng, bối cảnh tiếp xúc và khả năng vá.

CI thường nhận code từ pull request, nên dữ liệu do người ngoài sửa có thể đi vào shell script hoặc action. Workflow có quyền cao phải được thiết kế cẩn thận; không để code chưa tin cậy chạy cùng credential triển khai. Ưu tiên credential ngắn hạn theo cơ chế identity federation nếu nền tảng hỗ trợ, giới hạn quyền token và tách build/test khỏi deploy. Một pipeline chạy tự động nhưng không biết artifact nào được tạo từ commit nào khó kiểm soát hơn quy trình thủ công có bằng chứng.

### Lab kiểm tra pipeline

Trên repository thử nghiệm, liệt kê mọi secret và quyền workflow cần. Không in giá trị secret. Xem action/container nào do bên thứ ba cung cấp, phiên bản nào đang dùng và cách cập nhật an toàn. Thêm một kiểm tra dependency hoặc image scan theo tài liệu chính thức của công cụ bạn chọn; đọc ít nhất một cảnh báo và ghi lý do ưu tiên/không ưu tiên xử lý. Không chặn toàn bộ build bằng ngưỡng tùy tiện khi chưa hiểu độ nhiễu.

## Bài 3. Reliability, failure mode và phục hồi dữ liệu

Reliability là khả năng hệ thống thực hiện đúng chức năng khi người dùng cần. Một thiết kế đáng tin cậy bắt đầu bằng xác định service level mong muốn, failure modes và chi phí chấp nhận. Lỗi có thể là process crash, VM mất, database chậm, đĩa đầy, credential hết hạn, deploy sai hoặc lỗi người vận hành. Với mỗi lỗi, hỏi: tín hiệu nào phát hiện, phạm vi ảnh hưởng, thao tác giảm tác động và cách ngăn lặp lại.

Redundancy giúp vượt qua một số lỗi nhưng không tự động giải quyết lỗi cấu hình chung, xóa dữ liệu hoặc dependency chung. Autoscaling giúp khi tải tăng trong giới hạn, nhưng có thể làm quá tải database nếu không xem toàn chuỗi. Circuit breaker, timeout và retry có thể giúp chịu lỗi tạm thời; retry thiếu giới hạn có thể khuếch đại sự cố. Trước khi thêm cơ chế, mô tả rõ failure mode cần xử lý.

Backup, replication và snapshot có mục đích khác nhau. Backup là bản dữ liệu để phục hồi tại một thời điểm; replication giữ nhiều bản sao gần như liên tục; snapshot là cơ chế chụp trạng thái của một tài nguyên, cần hiểu tính nhất quán. Chính sách backup phải nêu tần suất, thời gian giữ, quyền, mã hóa và kiểm tra restore. RPO/RTO phải có căn cứ từ nhu cầu của ứng dụng. Nếu mất tối đa một giờ dữ liệu là chấp nhận được, một backup mỗi ngày sẽ không đáp ứng khi xảy ra sự cố gần cuối ngày.

### Lab restore thực tế

Tạo database thử với vài ghi chú giả. Ghi số bản ghi và một giá trị kiểm tra. Tạo backup theo tài liệu database bạn chọn, xóa hoặc thay đổi dữ liệu trong bản thử, restore vào một database thử khác, rồi so sánh số bản ghi và nội dung. Đo thời gian từ lúc bắt đầu restore đến khi API dùng được. Không thử trên dữ liệu thật. Nếu bản backup không mở được, ghi rõ lỗi thay vì đánh dấu mục tiêu đã đạt.

## Bài 4. Incident và quyết định kỹ thuật

Trong sự cố, người giỏi không đoán nhanh nhất mà giữ được chuỗi quan sát và thay đổi kiểm soát: xác nhận tác động, kiểm tra thay đổi gần đây, khoanh vùng, giảm ảnh hưởng, ghi timeline rồi phân tích sâu sau khi ổn định. Chia vai nếu nhiều người cùng xử lý: một người điều phối, một người chẩn đoán, một người cập nhật tình hình. Quy trình này đặc biệt quan trọng khi quyền thay đổi production cao.

Một quyết định kiến trúc cần ghi mục tiêu, bối cảnh, các lựa chọn hợp lý, lợi/hại, chi phí và điều kiện xem xét lại. Ví dụ: chọn database managed thay vì tự chạy trên VM vì nhóm nhỏ muốn giảm công việc backup/patching, đổi lại chi phí tiền cao hơn và phụ thuộc dịch vụ. Lập luận có dữ liệu và giới hạn sẽ có giá trị trong phỏng vấn hơn việc chỉ liệt kê công cụ.

## Bài 5. Threat model có thể kiểm tra được

Thay vì ghi chung "bảo mật tốt", hãy mô tả một tình huống: người ngoài tạo pull request sửa workflow để in biến môi trường. Tài sản bị đe dọa là credential CI. Đường đi là code chưa tin cậy -> runner -> token/secret -> hệ thống cloud. Biện pháp phòng là giảm quyền token, tách job dùng credential khỏi PR chưa tin cậy và dùng chính sách approval theo nền tảng. Cách phát hiện có thể là review workflow, audit log và cảnh báo hành vi token lạ. Khi nghi lộ, thu hồi/rotate credential và xem hành động đã thực hiện bằng nó.

Tình huống thứ hai: ứng dụng ghi toàn bộ HTTP header vào log, vô tình có bearer token. Biện pháp phòng là chỉ log trường cần thiết và lọc thông tin nhạy cảm. Nếu đã lộ, xóa/giới hạn truy cập log theo quy trình, rotate token, xác định ai đã truy cập và đánh giá tác động. Tình huống thứ ba: database mở public để "debug cho nhanh". Biện pháp phòng là đường private, firewall hẹp và truy cập quản trị tạm thời có ghi nhận. Những ví dụ này minh họa một quy tắc: giảm cả xác suất lẫn phạm vi thiệt hại, rồi chuẩn bị khả năng phát hiện và phục hồi.

### Bảng rủi ro tự lập

Tạo bốn cột: tài sản, tình huống, tác động, kiểm soát. Điền ít nhất năm dòng cho repo của bạn: source code, CI token, container image, database và backup. Sắp xếp ưu tiên theo tác động và khả năng xảy ra trong bối cảnh của bạn, không theo điểm số máy quét một cách máy móc. Với mỗi kiểm soát, ghi bằng chứng kiểm tra được, ví dụ policy CI, cấu hình network hoặc log restore.

## Bài 6. Backup và restore ứng dụng ghi chú

Ứng dụng mẫu dùng SQLite để lab đơn giản. File `lesson/labs/notes-api/backup_lab.py` dùng API backup của SQLite để tạo bản sao nhất quán rồi phục hồi sang file **khác**. Trước khi chạy, tạo ít nhất một ghi chú và dừng ứng dụng để bài học dễ quan sát. Chạy `python backup_lab.py` trong thư mục ứng dụng. Script từ chối nếu file backup hoặc file restore cũ đã tồn tại để tránh ghi đè; kiểm tra chúng trước khi quyết định xóa dữ liệu lab. Kết quả mong đợi là số ghi chú ở bản gốc và bản restore bằng nhau.

So sánh số lượng chưa đủ để bảo đảm mọi dữ liệu đúng. Hãy mở file phục hồi bằng một lệnh Python hoặc cho API chạy với `NOTES_DB` trỏ tới `restored-notes.db`, rồi gọi `GET /notes` và đối chiếu nội dung. Dừng bản API cũ trước nếu cùng dùng port 8000. Ghi thời gian bắt đầu và thời gian người dùng có thể đọc lại dữ liệu. Đó là RTO quan sát trong lab; không tự nhận là RTO production. Tạo thêm ghi chú sau backup nhưng trước restore để thấy dữ liệu mới này không có trong bản backup; khoảng mất dữ liệu đó minh họa RPO.

Lưu ý: backup cùng nằm trên một đĩa với dữ liệu gốc sẽ không giúp khi đĩa mất. Trong hệ thống thật, cần nơi lưu riêng, kiểm soát quyền, mã hóa phù hợp, retention và diễn tập restore định kỳ. Một script local đơn giản dạy quy trình, không thay thế chiến lược backup production.

## Bài 7. Diễn tập quyết định khi hệ thống lỗi

Giả sử sau deploy phiên bản B, 30% request tạo ghi chú trả 500; đọc ghi chú vẫn hoạt động. Một cách xử lý có trình tự: xác nhận dashboard/log và thời điểm; xem B thay đổi mã hay schema nào; thử một request có request ID; so sánh log B với A; cân nhắc rollback B nếu tương thích dữ liệu; kiểm tra tỷ lệ lỗi giảm và bản ghi không bị mất; cuối cùng phân tích lỗi và bổ sung test. Nếu migration của B đã đổi schema không tương thích, rollback image ngay có thể tệ hơn. Hãy ghi điểm chưa biết và dừng thay đổi dữ liệu cho tới khi hiểu.

Trong phỏng vấn, người đánh giá có thể cố tình không cho đủ dữ kiện. Câu trả lời tốt nêu dữ kiện cần thu thập và quyết định phụ thuộc vào chúng. Một câu "chỉ cần restart" không đủ vì restart có thể xóa triệu chứng tạm thời mà làm mất log/bằng chứng. Cũng không phải lúc nào root cause phải tìm trước khi khôi phục; hãy giảm ảnh hưởng trước nếu có hành động an toàn.

## Bài 8. Reliability là một chuỗi phụ thuộc

Một API có thể có ba replica nhưng vẫn phụ thuộc vào một database, một DNS service, một secret và một đường mạng. Vẽ dependency graph rồi hỏi mỗi cạnh: nếu phụ thuộc chậm, timeout ở đâu; nếu lỗi, có fallback không; retry có làm tải tăng không; có tín hiệu nào phát hiện không. Khi một request đi qua ba service mà mỗi service có xác suất thành công thấp hơn 100%, tổng khả năng thành công có thể thấp hơn từng phần. Không cần tính con số chính xác để thấy rằng thêm tầng có thể thêm failure mode.

Ví dụ người dùng nhấn Lưu, API gọi DB nhưng timeout. Nếu API retry ngay ba lần cho mọi request, DB đang quá tải có thể nhận gấp nhiều lần số truy vấn. Cách xử lý có thể là timeout hợp lý, retry giới hạn với backoff và chỉ retry thao tác an toàn/idempotent theo thiết kế. Nếu POST tạo ghi chú bị retry sau khi DB đã ghi nhưng response thất lạc, người dùng có thể có hai ghi chú. Idempotency key là một cách giải quyết khi nghiệp vụ cần; lab hiện tại chưa có, nên ghi rõ giới hạn.

### Bài tập failure mode

Liệt kê năm phụ thuộc của Notes API: process, file/volume, CPU/memory, network, client hoặc database service tương lai. Với mỗi phụ thuộc, ghi triệu chứng, tín hiệu, cách giảm tác động và cách khôi phục. Ví dụ volume đầy -> POST lỗi/SQLite ghi thất bại -> metric dung lượng + log -> ngừng ghi không cần thiết/giải phóng theo quy trình -> tăng dung lượng hoặc restore nếu data bị hỏng. Không tùy tiện xóa file database để lấy chỗ trống.

## Bài 9. Hiệu năng, năng lực tải và chi phí

Khi ứng dụng chậm, hãy đo trước khi tối ưu. Độ trễ có thể do CPU, I/O đĩa, database query, lock, mạng hoặc dependency. Mỗi nguyên nhân cần tín hiệu khác. Tăng CPU khi query chậm vì thiếu index có thể làm tốn tiền mà không giải quyết gốc. Với bài lab, tạo số lượng ghi chú lớn hơn và so sánh thời gian GET /notes; ghi cấu hình máy và số bản ghi, vì kết quả không có ngữ cảnh khó diễn giải.

Capacity planning bắt đầu bằng nhu cầu: request/giây, kích thước dữ liệu, tăng trưởng và peak. Thêm headroom để chịu biến động, nhưng tránh cấp tài nguyên quá dư. Một hệ thống có thể cần scale API nhưng không scale DB tuyến tính theo cùng cách. Chi phí cloud gồm compute, storage, network egress, logging/monitoring và tài nguyên quên xóa. Mọi quyết định reliability có giá: nhiều replica, backup thường xuyên và multi-zone đều cần tiền và vận hành. Hãy gắn chúng với SLO/RPO/RTO cụ thể.

### Mini review quyết định

Giả sử yêu cầu của dự án là 99,9% availability cho người dùng, mất tối đa 15 phút dữ liệu và khôi phục trong một giờ. Hãy nêu phần nào của kiến trúc/lab hiện tại chưa đáp ứng: một file SQLite trên máy cá nhân, backup thủ công, không có cảnh báo và không có người trực chắc chắn chưa đủ. Bạn không cần lập tức xây kiến trúc đắt tiền; nhiệm vụ là nhận ra khoảng cách giữa cam kết và bằng chứng.

## Cổng năng lực và câu hỏi phỏng vấn

Bạn vẽ được threat model đơn giản, cấp quyền hẹp cho workflow, phân biệt backup/replication, restore thành công trong lab, giải thích RPO/RTO, và viết quyết định kỹ thuật có tradeoff. Tự trả lời: Vì sao xóa secret khỏi commit mới chưa đủ? Tại sao thêm replica không cứu được lỗi schema? Nếu alert báo nhiều lỗi sau deploy, bước giảm tác động nào ưu tiên? Làm sao chứng minh backup dùng được?

## Tài liệu chính thức

- OWASP DevSecOps Guideline: https://owasp.org/www-project-devsecops-guideline/
- GitHub Actions security: https://docs.github.com/en/actions/security-for-github-actions
- OpenSSF Supply Chain guidance: https://openssf.org/
- Google Cloud Well-Architected Framework: https://docs.cloud.google.com/architecture/framework
- Google SRE Workbook: https://sre.google/workbook/table-of-contents/
