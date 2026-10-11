# Giai đoạn 1 - Hệ điều hành, mạng và ứng dụng cơ bản

Hãy dành thời gian ở giai đoạn này. Phần lớn lỗi triển khai trở nên dễ hiểu hơn khi bạn biết tiến trình chạy ở đâu, dữ liệu đi qua đường nào và ứng dụng phụ thuộc vào những gì. Mỗi bài có thể học qua nhiều buổi.

## Bài 1. Hệ điều hành và terminal

Hệ điều hành quản lý phần cứng và cung cấp môi trường cho chương trình chạy. Khi bạn mở một ứng dụng, hệ điều hành tạo tiến trình (process), cấp bộ nhớ và thời gian CPU, cho phép truy cập file và mạng theo quyền. Một server cũng là máy tính có hệ điều hành; khác biệt quan trọng là server thường chạy dịch vụ liên tục, nhận request từ máy khác và cần được theo dõi.

Đường dẫn cho biết vị trí file. Trên Linux, `/home/tenban/app/config.txt` dùng dấu `/` và bắt đầu từ gốc `/`. Trên Windows, `C:\Users\...` bắt đầu từ ổ đĩa. Thư mục hiện tại ảnh hưởng đến cách chương trình tìm file tương đối. Khi lệnh báo "không tìm thấy file", hãy kiểm tra thư mục hiện tại và đường dẫn trước khi sửa mã.

Trong Linux, quyền đọc (r), ghi (w) và thực thi (x) được áp cho chủ sở hữu, nhóm và người khác. Một script có thể tồn tại nhưng không được chạy vì thiếu quyền x, hoặc dịch vụ không đọc được cấu hình vì chủ sở hữu sai. Không dùng quyền root làm cách chữa mặc định: cần xác định tiến trình chạy dưới user nào và cấp quyền hẹp đủ dùng.

Service là tiến trình được quản lý để chạy nền. Trên nhiều bản phân phối Linux, `systemd` quản lý vòng đời service: khởi động, dừng, tự chạy lại và ghi log. Khi service lỗi, chuỗi suy luận là: trạng thái -> log -> cấu hình -> quyền -> phụ thuộc -> tài nguyên. Chỉ restart liên tục sẽ che dấu nguyên nhân.

### Lab đọc-only trên Linux/WSL

Điều kiện: có terminal Linux hoặc WSL. Chạy từng lệnh và tự dự đoán kết quả trước khi xem: `pwd`, `ls -la`, `whoami`, `id`, `ps aux`, `df -h`, `free -h`. `pwd` cho vị trí hiện tại; `ls -la` cho file ẩn và quyền; `whoami`/`id` cho danh tính; `ps` cho tiến trình; hai lệnh cuối cho dung lượng đĩa và bộ nhớ. Một số môi trường WSL có thể hiển thị thông tin bộ nhớ khác máy Windows chính.

Ghi ít nhất ba phát hiện: user hiện tại là ai, thư mục hiện tại ở đâu, phân vùng nào chứa thư mục đó. Không cần gửi toàn bộ danh sách tiến trình hoặc thông tin nhạy cảm. Nếu máy chỉ có PowerShell, dùng `Get-Location`, `Get-ChildItem -Force`, `whoami`, `Get-Process`, `Get-PSDrive` để học cùng ý tưởng.

### Tình huống điều tra

Dịch vụ không ghi được file log. Giả thuyết có thể là thư mục không tồn tại, quyền sai, đĩa đầy hoặc cấu hình log trỏ tới đường dẫn khác. Hãy viết thứ tự kiểm tra ít tác động nhất. Đáp án gợi ý: xác định user của service và đường dẫn log thực tế; xem quyền thư mục; xem dung lượng; đọc thông báo lỗi; chỉ sau đó thay đổi quyền hoặc cấu hình có kiểm soát.

## Bài 2. Mạng: request đi từ máy bạn đến dịch vụ như thế nào?

IP là địa chỉ của thiết bị trong một mạng. Port giúp máy phân biệt dịch vụ nào nhận kết nối. DNS đổi tên miền thành địa chỉ IP. TCP giúp hai đầu trao đổi dữ liệu có thứ tự và báo lỗi truyền; HTTP là ngôn ngữ request/response ở tầng ứng dụng. TLS bảo vệ kênh truyền và xác thực máy chủ theo chứng chỉ. Một URL như `https://example.com:443/notes` chứa scheme, host, port và path. Port 443 là mặc định của HTTPS nên thường không hiện.

Khi bạn mở URL, máy cần tìm IP của tên miền, tạo kết nối tới IP:port, thỏa thuận TLS nếu dùng HTTPS, gửi HTTP request, rồi nhận response. Một lỗi có thể xảy ra ở từng bước. `NXDOMAIN` gợi ý vấn đề tên miền; timeout gợi ý đường mạng/firewall/dịch vụ không đáp ứng; `connection refused` gợi ý không có tiến trình lắng nghe hoặc bị từ chối ngay; HTTP 404 nghĩa là đã nhận phản hồi HTTP nhưng path không được tìm thấy; HTTP 500 gợi ý phía server xử lý thất bại. Đây là chỉ dẫn ban đầu, cần đối chiếu log và cấu hình.

Địa chỉ `127.0.0.1` hoặc `localhost` trỏ tới chính máy đang chạy lệnh. Nếu ứng dụng trong container hoặc VM, `localhost` ở đó là container/VM đó, không tự động là máy chủ hay máy của bạn. Rất nhiều lỗi kết nối database xuất phát từ hiểu nhầm phạm vi của `localhost`.

### Lab quan sát một request

Điều kiện: có trình duyệt và terminal. Mở trang web công khai bạn tin tưởng. Trong browser, mở Developer Tools -> Network, tải lại trang, chọn một request. Ghi method, URL, status code và thời gian. Trên PowerShell, có thể dùng `Test-NetConnection example.com -Port 443`; trên Linux dùng `curl -I https://example.com`. Không gộp lỗi DNS, TCP và HTTP thành một "lỗi mạng"; ghi bước cụ thể thất bại.

### Bài tập luồng request

Vẽ bằng chữ: browser -> DNS -> internet/router -> reverse proxy/load balancer -> ứng dụng -> database. Đánh dấu ở đâu có IP, port, TLS và HTTP. Nếu browser nhận HTTP 502, bạn sẽ xem proxy/upstream; nếu nhận HTTP 200 nhưng dữ liệu rỗng, bạn sẽ xem mã ứng dụng và truy vấn database trước.

## Bài 3. Git và lịch sử thay đổi

Git lưu lịch sử các snapshot của dự án. Working tree là file bạn đang sửa; staging area là tập thay đổi chuẩn bị đưa vào commit; commit là một mốc có định danh. Branch giúp tách luồng công việc. Remote là bản repository ở nơi khác, ví dụ máy chủ Git; `push` gửi commit lên remote, `pull` nhận thay đổi về. Git không tự quyết định rằng mọi file nên được đưa lên mạng: bạn phải kiểm tra trước khi commit, đặc biệt với secrets và file môi trường.

Quy trình tối thiểu: xem trạng thái -> sửa file -> xem diff -> stage đúng file -> commit với thông điệp rõ -> đẩy lên nhánh -> review. `git status` và `git diff` là hai lệnh nên chạy thường xuyên. Khi có conflict, Git cần bạn chọn nội dung cuối cùng; đừng xóa các dấu conflict mà không hiểu hai thay đổi đang tranh nhau điều gì.

### Lab Git local

Điều kiện: đã cài Git. Trong một thư mục thử nghiệm mới, chạy `git init`, tạo `notes.txt`, rồi chạy `git status`. Thêm một dòng, chạy `git add notes.txt`, `git diff --cached`, `git commit -m "Add first note"` và `git log --oneline`. Nếu Git yêu cầu cấu hình tên/email, đọc hướng dẫn của Git trước khi cấu hình; tên và email commit có thể hiện trong lịch sử. Không dùng repository chứa dữ liệu riêng tư để thử `push`.

Mục tiêu của lab không phải thuộc lệnh. Hãy giải thích vì sao `git diff` trước stage và `git diff --cached` sau stage cho hai góc nhìn khác nhau. Thử sửa file thêm lần nữa sau commit và quan sát `git status`.

## Bài 4. Scripting, ứng dụng và database

Script là chương trình nhỏ tự động hóa công việc. Một script tốt có input rõ, kiểm tra lỗi, mã thoát (exit code) đáng tin, không in bí mật và có thể chạy lại mà không gây hại. Bắt đầu bằng bài toán cụ thể: kiểm tra một URL có phản hồi hay không; ghi thời điểm và status; trả mã 0 khi đúng, khác 0 khi lỗi. Trước khi dùng script trong CI, hãy tự chạy và kiểm tra trường hợp thành công lẫn thất bại.

Ứng dụng thường nhận cấu hình qua biến môi trường hoặc file cấu hình, kết nối tới database và ghi log. Cùng một mã nguồn có thể chạy ở local/test/production với cấu hình khác nhau. Không đặt mật khẩu trực tiếp trong mã hoặc commit file `.env` chứa bí mật. Health endpoint chỉ nên nói ứng dụng có thể đáp ứng điều gì; kiểm tra quá nặng có thể làm tình trạng xấu hơn.

Database quan hệ lưu dữ liệu trong bảng; mỗi hàng là một bản ghi, mỗi cột là thuộc tính. SQL `SELECT` đọc, `INSERT` thêm, `UPDATE` sửa, `DELETE` xóa. Một giao dịch (transaction) nhóm nhiều thao tác để giữ dữ liệu nhất quán theo quy tắc database. Backup chỉ có giá trị khi đã thử restore. Khi triển khai phiên bản mới, thay đổi schema có thể không tương thích với phiên bản cũ, nên cần nghĩ đến rollback trước khi migration.

### Bài tập thiết kế ứng dụng mẫu

Ứng dụng xuyên suốt sẽ là API ghi chú đơn giản: tạo ghi chú, liệt kê và kiểm tra sức khỏe. Vẽ bốn thành phần: client, API, database, nơi chứa log. Ghi data nào cần tồn tại sau restart và data nào không. Hãy tự chọn Python, Node.js hoặc ngôn ngữ bạn muốn học; mục tiêu DevOps là hiểu đủ mã để chạy và kiểm tra, không cần xây sản phẩm lớn ngay.

## Bài 5. Thực hành ứng dụng mẫu từ đầu đến cuối

Để các bài sau có một đối tượng chung, tài liệu kèm một Notes API nhỏ ở `lesson/labs/notes-api/app.py`. Nó dùng thư viện chuẩn Python và SQLite; không cần cài framework web hay database server. Đây là ứng dụng học tập, không phải mẫu triển khai production. Khi đọc code, đừng cố nhớ từng dòng: trước tiên tìm nơi mở cổng, nơi nhận request và nơi lưu dữ liệu.

### Chuẩn bị và chạy

Điều kiện: Python 3 đã được cài, bạn có quyền tạo file trong thư mục lab. Mở terminal ở `lesson/labs/notes-api`. Chạy `python --version` hoặc `py --version` trên Windows để xác nhận trình thông dịch. Nếu báo không nhận ra lệnh, dừng lab và cài Python từ nguồn chính thức hoặc nhờ Codex hướng dẫn theo hệ điều hành của bạn. Khi Python đã sẵn sàng, chạy `python app.py` (Windows có thể là `py app.py`). Terminal sẽ in địa chỉ `http://127.0.0.1:8000`. Giữ cửa sổ này mở.

Ở terminal thứ hai, chạy `curl http://127.0.0.1:8000/health` trên Linux/macOS. PowerShell có thể dùng `Invoke-RestMethod http://127.0.0.1:8000/health`. Kết quả mong đợi có `status: ok` và `version: lab-1`. Nếu kết nối thất bại, kiểm tra terminal thứ nhất còn chạy không, cổng 8000 có bị ứng dụng khác chiếm không, và bạn có gõ đúng `127.0.0.1` không. Không thay nhiều thứ cùng lúc.

Trên PowerShell, thử tạo ghi chú bằng `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/notes -ContentType 'application/json' -Body '{"body":"Ghi chu dau tien"}'`. Trên Linux/macOS, dùng `curl -X POST http://127.0.0.1:8000/notes -H 'Content-Type: application/json' -d '{"body":"Ghi chu dau tien"}'`. Kết quả mong đợi là HTTP 201 với `id` và nội dung. Gọi `GET /notes` để thấy bản ghi. Thử gửi `{}` và dự đoán HTTP status trước khi xem: ứng dụng trả 400 vì thiếu `body`.

Dừng ứng dụng bằng Ctrl+C rồi chạy lại. Gọi `GET /notes`; ghi chú vẫn còn vì SQLite ghi vào `notes.db`. Tạm đổi tên file này trong lab rồi chạy lại; danh sách trở nên rỗng vì ứng dụng mở database mới. Khôi phục tên file cũ để lấy lại dữ liệu. Thí nghiệm này giúp bạn phân biệt dữ liệu nằm trong bộ nhớ tiến trình với dữ liệu lưu bền trên đĩa. Đừng đổi tên file database của ứng dụng thật khi chưa có backup.

### Đọc một request xuyên các lớp

Khi gọi `GET /notes`, chương trình client tạo HTTP request tới địa chỉ loopback `127.0.0.1` và port 8000. Hệ điều hành chuyển kết nối đến tiến trình Python đang lắng nghe. Handler đọc path `/notes`, mở SQLite, chạy câu `SELECT`, chuyển các hàng thành JSON rồi gửi HTTP response. Hãy vẽ chuỗi này lên giấy và đánh dấu: IP, port, process, file database, SQL, JSON và status code. Sau đó giải thích vì sao `GET /unknown` trả 404 dù server đang chạy tốt.

Log in ở terminal thứ nhất cho biết request và status. So sánh log khi gọi `/health`, `/notes` và `/unknown`. Nếu terminal không hiện request, lỗi có thể xảy ra trước khi request tới tiến trình: client gọi sai host/port hoặc server không chạy. Nếu log hiện 500, request đã tới ứng dụng và bạn cần xem exception. Đây là cách đầu tiên dùng log để phân lớp lỗi.

### Bài tập xử lý lỗi có hướng dẫn

Tình huống A: ứng dụng báo cổng đã được sử dụng. Trước hết xác nhận một bản `app.py` khác có đang chạy không. Nếu có, dừng bản cũ bằng Ctrl+C. Nếu không, có thể chạy lab ở cổng khác bằng cách đặt biến `NOTES_PORT` trong môi trường rồi khởi động lại. Đừng tắt một tiến trình lạ chỉ vì nó dùng cùng cổng.

Tình huống B: `GET /health` hoạt động nhưng `POST /notes` trả 400. Điều này cho biết mạng và process cơ bản hoạt động. Với ứng dụng lab hiện tại, kiểm tra JSON body, key `body` và giới hạn nội dung; code chưa kiểm tra header `Content-Type` dù client nên gửi `application/json`. Đừng sửa DNS hoặc firewall khi request đã được API trả 400.

Tình huống C: ghi chú mất sau khi xóa thư mục lab. Ứng dụng lưu vào `notes.db` trong thư mục hiện tại theo mặc định. Đây là lý do lệnh được chạy từ đâu quan trọng. Bạn có thể chỉ định đường dẫn rõ qua biến `NOTES_DB`, nhưng hãy ghi lại vị trí và sao lưu trước khi xóa môi trường.

### Kiểm tra hiểu sâu

1. Nếu gọi `127.0.0.1:8001` trong khi ứng dụng nghe 8000, lớp nào sai?
2. Nếu `/health` trả 200 nhưng `/notes` lỗi do database, health endpoint đã chứng minh được điều gì và chưa chứng minh được điều gì?
3. Vì sao thao tác thêm ghi chú dùng POST còn liệt kê dùng GET?
4. Vì sao truy vấn SQL trong code dùng tham số `?` thay vì ghép trực tiếp chuỗi người dùng? Gợi ý: tránh SQL injection và vấn đề escaping.

Đáp án định hướng: (1) cổng của kết nối; (2) tiến trình có thể trả lời health, chưa chứng minh đường database; (3) GET đọc, POST tạo tài nguyên theo API đơn giản này; (4) câu lệnh tham số tách dữ liệu khỏi cấu trúc SQL. Hãy trả lời bằng lời của mình trước khi xem gợi ý.

## Bài 6. Điều tra một lỗi mạng theo từng lớp

Khi người dùng nói "không vào được ứng dụng", một người mới thường thử đổi DNS, mở firewall hoặc restart server ngay. Cách có hệ thống bắt đầu từ việc xác định **điểm cuối đã chứng minh hoạt động**. Nếu `GET /health` từ máy chủ trả 200 nhưng từ máy người dùng timeout, ứng dụng có thể ổn và vấn đề nằm trên đường mạng. Nếu từ cả hai nơi đều trả HTTP 500, request đã đi tới ứng dụng và cần xem log hoặc dependency. Nếu trình duyệt báo lỗi chứng chỉ, TLS là lớp cần kiểm tra trước khi đụng database.

Hãy chia chuỗi thành sáu câu hỏi: tên miền phân giải thành IP nào; có đi được đến IP/port không; có hoàn tất TLS không; HTTP request có tới proxy không; proxy có chuyển đến ứng dụng không; ứng dụng có đọc được database không. Mỗi câu có một loại bằng chứng. DNS dùng lookup; TCP dùng kiểm tra kết nối; TLS dùng thông tin certificate và handshake; HTTP dùng status/header; ứng dụng dùng log; database dùng log/kết nối. Không một lệnh nào chứng minh toàn bộ chuỗi.

### Lab với server local

Điều kiện: Python và một terminal. Tạo thư mục lab trống, mở terminal ở đó, chạy `python -m http.server 8001` (Windows có thể dùng `py -m http.server 8001`). Mở `http://127.0.0.1:8001` trong trình duyệt; mong đợi trang liệt kê thư mục. Khi server đang chạy, thử `http://127.0.0.1:8002`; dự đoán lỗi. Quay về terminal, quan sát request log. Dừng server bằng Ctrl+C rồi mở lại URL 8001; dự đoán lỗi mới. Bài này chứng minh vai trò của process và port mà chưa cần cloud.

Thử thêm `http://localhost:8001` khi server chạy. Trên nhiều máy nó tới cùng dịch vụ qua tên loopback, nhưng cách phân giải IPv4/IPv6 có thể khác. Nếu hai URL không cho cùng kết quả, đây là cơ hội quan sát DNS/hosts và địa chỉ server đang bind, không phải lỗi cần che bằng một cấu hình đoán mò.

### Tình huống có lời giải thích

Bạn thấy trình duyệt nhận 404 từ Notes API ở `/unknown`. Điều gì đã hoạt động? Ít nhất client tới được IP/port và tiến trình đã trả HTTP response. Lỗi có thể là path không tồn tại. Bạn thấy timeout không có log trên server: request có thể chưa tới ứng dụng; kiểm tra client, cổng, firewall hoặc proxy. Bạn thấy 500 và log nêu SQLite không mở được file: kiểm tra đường dẫn và quyền file database. Ba tình huống giống nhau ở cảm giác "ứng dụng hỏng" nhưng dẫn đến ba nhánh điều tra khác.

## Bài 7. Một vòng Git có conflict được giải quyết đúng cách

Ở Giai đoạn 1, bạn cần hiểu commit và branch trước khi có CI. Tạo hai branch từ cùng một commit trong repository **thử nghiệm**. Trên branch thứ nhất, sửa dòng đầu của `notes.txt` thành "Mục tiêu: học Linux" rồi commit. Trở về branch gốc, tạo branch thứ hai từ commit ban đầu, sửa chính dòng đó thành "Mục tiêu: học networking" rồi commit. Khi merge branch thứ nhất vào branch thứ hai, Git có thể báo conflict vì hai nhánh sửa cùng vị trí. Mở file để xem phần nội dung của mỗi bên, quyết định nội dung cuối và viết lại một dòng rõ nghĩa, ví dụ "Mục tiêu: học Linux và networking". Sau đó stage và commit kết quả merge.

Điểm học không phải nhớ ký hiệu conflict. Bạn phải biết vì sao nó xuất hiện: Git không thể tự chọn giữa hai ý định. Nếu chỉ xóa ký hiệu mà không đọc hai thay đổi, có thể đánh mất nội dung. Trong team, hỏi tác giả hoặc đọc issue/PR nếu ý định không rõ. Sau merge, chạy test/đọc file để xác nhận kết quả, vì code hợp nhất có thể đúng cú pháp nhưng sai hành vi.

### Tự kiểm tra Git

`git status` nói file nào thay đổi; `git diff` cho thay đổi chưa stage; `git diff --cached` cho thay đổi sẽ vào commit; `git log --oneline` cho lịch sử. Nếu lỡ thêm một file chứa secret vào staging nhưng chưa commit, hãy bỏ file đó khỏi staging theo tài liệu Git rồi kiểm tra lại status. Nếu secret đã được push, coi nó đã lộ và rotate; sửa lịch sử đơn thuần không đủ để bảo đảm bí mật an toàn.

## Bài 8. Đọc script và truy vấn SQL như người vận hành

Một script kiểm tra dịch vụ cần trả exit code đáng tin. Trong nhiều shell, 0 biểu thị thành công và số khác 0 biểu thị lỗi. CI dựa vào mã thoát để quyết định job xanh hay đỏ; in chữ "ERROR" rồi trả 0 có thể khiến pipeline tưởng mọi thứ ổn. Script cũng cần timeout: nếu request treo mãi, pipeline và công việc vận hành bị kẹt. Khi có retry, nên giới hạn số lần và khoảng chờ; retry vô hạn có thể che sự cố.

Code Notes API dùng câu `SELECT id, body FROM notes ORDER BY id` để đọc; `INSERT INTO notes (body) VALUES (?)` để thêm. Dấu `?` là tham số của SQLite, giúp tách dữ liệu người dùng khỏi cú pháp SQL. Nếu ghép trực tiếp `body` vào chuỗi truy vấn, một input có dấu nháy có thể làm hỏng cú pháp và input độc hại có thể thay đổi ý nghĩa truy vấn. Khi đọc code ứng dụng, hãy xác định query nào đọc, query nào ghi, file dữ liệu ở đâu và lỗi database được log thế nào.

Một transaction có ý nghĩa khi nhiều thay đổi phải nhất quán. Ví dụ tạo đơn hàng gồm dòng hàng và cập nhật số lượng tồn: nếu dòng hàng được ghi nhưng cập nhật tồn thất bại, database có thể rơi vào trạng thái sai nếu không quản lý giao dịch. Notes API chỉ thêm một hàng nên ví dụ đơn giản. Ở giai đoạn sau, bạn sẽ thấy tại sao migration database cần tính tới phiên bản ứng dụng cũ và mới.

### Bài tập mở rộng app có kiểm soát

Thêm endpoint `GET /version` trả version hiện tại từ biến môi trường. Trước khi sửa, viết kết quả mong đợi; sau khi sửa, gọi endpoint và kiểm tra status/body. Sau đó cố ý không đặt biến môi trường để xem default. Đây là bài tập tự làm, không cần đưa ngay lên cloud. Nếu bạn chưa tự tin sửa Python, hãy nhờ Codex hướng dẫn từng dòng và yêu cầu nó giải thích thay đổi trước khi áp dụng.

## Cổng năng lực và câu hỏi phỏng vấn

Bạn nên tự trả lời được: service khác process ở điểm nào? DNS giải quyết bước gì? Tại sao HTTP 500 cho biết đã đi xa hơn lỗi DNS? Git commit khác push thế nào? Vì sao container restart có thể làm mất dữ liệu nếu lưu sai chỗ? Khi chưa chắc, hãy làm lại lab nhỏ và ghi bằng chứng thay vì học thuộc đáp án.

## Tài liệu chính thức

- Git book: https://git-scm.com/book/en/v2
- MDN HTTP overview: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview
- PostgreSQL tutorial: https://www.postgresql.org/docs/current/tutorial.html
- Microsoft WSL install: https://learn.microsoft.com/windows/wsl/install
