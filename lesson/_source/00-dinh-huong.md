# Giai đoạn 0 - Định hướng và chuẩn bị học DevOps

Tập bài giảng này dành cho người bắt đầu từ con số 0. Đọc theo thứ tự, tự làm các bài tập nhỏ và ghi lại điều đã quan sát. Bạn không cần nhớ mọi thuật ngữ sau lần đọc đầu. Mục tiêu của tuần này là biết mình sẽ xây gì, học để giải quyết vấn đề nào và có một môi trường học an toàn.

## Bài 1. DevOps giải quyết vấn đề gì?

Một ứng dụng không kết thúc khi lập trình viên viết xong mã. Mã phải được kiểm tra, đóng gói, đưa lên môi trường chạy, cấu hình, giám sát, sửa khi có lỗi và cập nhật nhiều lần. Nếu mỗi bước chỉ nằm trong đầu một người, việc phát hành chậm và dễ sai. DevOps là tập hợp cách làm giúp nhóm phát triển và vận hành phối hợp để đưa thay đổi tới người dùng một cách thường xuyên, an toàn và có thể quan sát được. Từ này không chỉ tên một phần mềm hay một chứng chỉ.

Hãy tưởng tượng một dịch vụ ghi chú. Người dùng bấm Lưu nhưng dữ liệu không xuất hiện. Lỗi có thể nằm ở giao diện, API, database, mạng, cấu hình, quyền truy cập hoặc bản phát hành vừa được đưa lên. Người làm DevOps cần hiểu đường đi của thay đổi và của một request, biết xem tín hiệu, thu hẹp phạm vi nghi vấn và khôi phục dịch vụ. Họ thường xây công cụ tự động để nhóm tránh lặp lỗi cũ.

Một vòng đời đơn giản là: lập kế hoạch -> viết mã -> kiểm tra -> đóng gói -> phát hành -> vận hành -> quan sát -> học từ phản hồi. Các mũi tên quan trọng như từng ô: nếu một bản sửa đã được kiểm tra nhưng người vận hành không biết phiên bản nào đang chạy, vòng đời vẫn có lỗ hổng. Nếu có dashboard đẹp nhưng không thể rollback, sự cố vẫn kéo dài.

### Ví dụ có giải thích

Giả sử phiên bản 1 trả về danh sách ghi chú. Phiên bản 2 thêm chức năng tìm kiếm. Trước khi phát hành, nhóm chạy test; nếu test qua, pipeline tạo một artifact có định danh; hệ thống triển khai artifact ấy; một smoke test xác nhận API còn trả kết quả; người vận hành nhìn lỗi và độ trễ; nếu nhiều request thất bại, hệ thống có thể quay về phiên bản 1. Mỗi bước có bằng chứng. Khả năng trả lời "đang chạy phiên bản nào?", "lỗi xuất hiện từ khi nào?" và "làm sao phục hồi?" là dấu hiệu của quy trình tốt.

### Tự kiểm tra

1. Vì sao một ứng dụng chạy được trên máy của lập trình viên vẫn có thể lỗi khi triển khai?
2. Tự động hóa giúp ích gì nếu thiếu kiểm tra và quan sát?
3. Trong ví dụ trên, artifact khác mã nguồn ở điểm nào?

Gợi ý: artifact là kết quả build có thể triển khai, ví dụ image container; mã nguồn là đầu vào. Tự động hóa một quy trình sai có thể khiến lỗi lặp lại nhanh hơn.

## Bài 2. Các vai trò và cách chọn hướng học

DevOps Engineer thường chú ý toàn bộ đường đi từ commit đến môi trường chạy: Git, CI/CD, hạ tầng, triển khai và vận hành. Cloud Engineer tập trung thiết kế và quản lý các dịch vụ trên cloud, đặc biệt mạng, IAM, compute, storage và chi phí. SRE tập trung độ tin cậy đo được bằng tín hiệu người dùng, SLO, cảnh báo và xử lý sự cố. Platform Engineer xây nền tảng tự phục vụ để nhóm phát triển dùng các khả năng trên một cách nhất quán. Một công ty nhỏ có thể gộp nhiều vai trò; công ty lớn có thể tách rõ.

Với mục tiêu hiện tại, ta lấy DevOps Engineer làm trục chính. Điều đó có nghĩa bạn cần hiểu ứng dụng đủ để đọc log và test, hiểu Linux và mạng đủ để chẩn đoán, hiểu cloud và hạ tầng đủ để triển khai, rồi học cách cải thiện độ tin cậy. Sau khi làm một dự án hoàn chỉnh, bạn có thể chọn nhánh Cloud, SRE hoặc Platform để đào sâu.

Đừng chọn công cụ chỉ vì tin tuyển dụng có tên đó. Hãy hỏi: hệ thống đang gặp khó khăn gì, công cụ nào giải quyết được, chi phí và độ phức tạp thêm vào là bao nhiêu? Một ứng dụng nhỏ có thể chạy tốt trên một VM hoặc dịch vụ managed; Kubernetes chưa chắc cần thiết. Khả năng chọn giải pháp vừa đủ là một kỹ năng chuyên môn.

### Bài tập

Viết ba câu: (1) kiểu hệ thống bạn muốn xây, (2) điều bạn muốn tự làm được sau ba tháng đầu, (3) loại sự cố bạn muốn biết cách điều tra. Chưa cần đúng thuật ngữ. Câu trả lời này giúp cá nhân hóa bài thực hành.

## Bài 3. Chuẩn bị môi trường và cách ghi nhật ký

"Terminal" là cửa sổ nhận lệnh dạng chữ. Trên Windows, PowerShell là terminal/shell phổ biến; Linux thường dùng Bash hoặc shell tương tự. Ta học cả khái niệm chung và điểm khác nhau về cú pháp. WSL cho phép chạy môi trường Linux trên Windows; đây là lựa chọn thuận tiện cho lab Linux, nhưng chỉ cài khi máy đáp ứng điều kiện và bạn muốn dùng. Không cần cài mọi công cụ trong một ngày.

Một "repository" là nơi lưu mã và lịch sử thay đổi. Trong khóa học, repository này sẽ chứa ghi chú, bài lab và dự án mẫu. Mỗi lần làm lab, ghi: mục tiêu, môi trường/phiên bản, lệnh đã chạy, kết quả thực tế, lỗi gặp, cách sửa và điều còn chưa hiểu. Không sao chép mật khẩu, token hoặc private key vào nhật ký. Ảnh chụp màn hình và log cũng có thể lộ bí mật.

### Lab an toàn đầu tiên

Điều kiện: bạn có quyền mở PowerShell hoặc terminal trên máy. Các lệnh dưới đây chỉ đọc thông tin; không cài phần mềm và không sửa dữ liệu.

Trên PowerShell, gõ lần lượt: `Get-Location`, `Get-ChildItem`, `$PSVersionTable.PSVersion`. `Get-Location` cho biết thư mục hiện tại. `Get-ChildItem` liệt kê mục trong thư mục. Lệnh cuối cho biết phiên bản PowerShell. Nếu dùng Linux, các lệnh tương ứng là `pwd`, `ls`, `uname -a` (lệnh cuối cho biết thông tin hệ thống, không phải phiên bản shell).

Quan sát đường dẫn đang đứng trước khi chạy lệnh tiếp theo. Đừng thử lệnh xóa để "xem điều gì xảy ra". Khi học DevOps, thói quen xác nhận môi trường và đích tác động quan trọng hơn tốc độ gõ.

Ghi một dòng vào nhật ký: hệ điều hành, terminal, lệnh đã chạy và điều bạn thấy. Nếu một lệnh báo "not recognized" hoặc "command not found", ghi nguyên văn thông báo; đó là thông tin chẩn đoán hữu ích.

### Lịch tuần đầu gợi ý

Buổi 1: đọc Bài 1 và vẽ vòng đời phần mềm bằng lời của mình. Buổi 2: đọc Bài 2, chọn vai trò tạm thời. Buổi 3: thực hiện lab terminal và ghi nhật ký. Buổi 4: cùng Codex xem hồ sơ, chọn ứng dụng mẫu, ngân sách lab và lịch học. Mỗi buổi có thể dài 45-90 phút tùy thời gian; không cần ép hoàn thành trong đúng một tuần.

## Bài 4. Đọc sơ đồ một hệ thống trước khi học công cụ

Ta dùng một ứng dụng ghi chú làm câu chuyện xuyên suốt. Người dùng mở trình duyệt, nhập nội dung và bấm Lưu. Trình duyệt gửi một request đến API. API kiểm tra nội dung và yêu cầu database ghi dữ liệu. Database trả kết quả; API trả response; trình duyệt hiển thị ghi chú. Ở thời điểm này chưa cần biết cách lập trình API. Điều cần hiểu là mỗi hộp có một nhiệm vụ và giữa các hộp có kết nối.

Khi hệ thống chạy trên máy của bạn, trình duyệt, API và database có thể cùng ở một máy. Khi chạy trên cloud, chúng có thể nằm ở nhiều máy hoặc dịch vụ khác nhau. Mã ứng dụng không tự tạo được quyền mạng và quyền database. Người học DevOps cần hiểu các điểm nối để biết lỗi xuất hiện ở bước nào. Đây là lý do roadmap bắt đầu bằng hệ điều hành, mạng và Git trước khi học Kubernetes.

Hãy xét ba triệu chứng khác nhau. (1) Trình duyệt không mở được trang: có thể tên miền, mạng hoặc server. (2) Trang mở nhưng bấm Lưu báo lỗi: có thể API, cấu hình database hoặc dữ liệu đầu vào. (3) Bấm Lưu thành công nhưng sau khi restart ghi chú biến mất: có thể dữ liệu chỉ nằm trong bộ nhớ hoặc container tạm. Một người xử lý tốt không đổi cấu hình ngẫu nhiên; họ hỏi câu nào phân biệt được các giả thuyết này.

### Bài tập có đáp án hướng dẫn

Giả sử người dùng báo "ứng dụng hỏng". Viết ba câu hỏi bạn sẽ hỏi trước khi sửa. Một câu trả lời hợp lý: bắt đầu hỏng từ khi nào; chức năng nào bị ảnh hưởng và có bao nhiêu người gặp; có thay đổi/deploy nào ngay trước đó không. Ba câu này giúp xác định tác động và mối liên hệ thời gian. Sau đó mới xem log, status và đường request. Câu trả lời khác cũng có thể tốt nếu giúp thu hẹp vấn đề mà không gây thay đổi hệ thống.

## Bài 5. Cách tự học một công nghệ mới

Trong DevOps, bạn sẽ liên tục gặp tên công cụ mới. Cách học bền vững là tách **khái niệm**, **cách công cụ thực hiện khái niệm**, và **cú pháp phiên bản hiện tại**. Ví dụ, "dịch vụ cần một địa chỉ ổn định" là vấn đề; Kubernetes Service là một cách giải; tên trường YAML và hành vi phiên bản cụ thể là chi tiết cần tra tài liệu. Nếu học ngược bằng cách chép YAML, bạn có thể chạy được demo nhưng không chẩn đoán được khi nó lỗi.

Mỗi khi gặp thuật ngữ, tạo một thẻ ghi chú năm dòng: nó là gì; giải quyết vấn đề nào; đầu vào/đầu ra; dấu hiệu hoạt động đúng; lỗi thường gặp. Ví dụ với DNS: DNS ánh xạ tên sang địa chỉ; giúp con người dùng tên dễ nhớ; đầu vào là tên, đầu ra thường là bản ghi địa chỉ; kiểm tra bằng công cụ lookup; lỗi thường gặp là record sai hoặc cache chưa cập nhật. Thẻ này chưa đầy đủ nhưng tạo khung để đặt câu hỏi đúng.

Áp dụng phương pháp "dự đoán rồi quan sát" khi làm lab. Trước lệnh `Get-Location`, hãy dự đoán nó trả về gì. Sau khi chạy, so sánh và ghi một câu giải thích. Nếu dự đoán sai, đó là nơi cần học tiếp. Không cần che lỗi khỏi nhật ký; lỗi có giải thích thường hữu ích hơn việc chỉ lưu ảnh màn hình xanh.

### Mẫu ghi nhật ký một buổi học

```text
Ngay: [ngay hoc]
Muc tieu: Biet terminal dang o thu muc nao
Du doan: Get-Location se in duong dan thu muc hien tai
Lenh da chay: Get-Location
Ket qua thuc te: [chep duong dan cua ban, bo thong tin rieng neu chia se]
Giai thich: Shell chay lenh trong thu muc nay neu dung duong dan tuong doi
Thac mac: Khi doi thu muc, lenh tim file thay doi the nao?
Buoc tiep: Thu Get-ChildItem o hai thu muc khac nhau
```

Ở ví dụ này, các dấu ngoặc vuông là chỗ bạn tự điền. Đừng viết "đã hiểu" nếu chưa giải thích được kết quả. Đây không phải bài chấm điểm; nó là bằng chứng cho lần ôn sau.

## Bài 6. Thiết lập hồ sơ và lịch học thực tế

Điền vào `learning/PROGRESS.md`: mục tiêu vai trò, thời gian học thực tế mỗi tuần, hệ điều hành, kinh nghiệm đã xác nhận, lựa chọn cloud tạm thời hoặc "chưa chọn", giới hạn ngân sách và ứng dụng mẫu. Nếu bạn có 6 giờ/tuần, hãy chia thành ba buổi 2 giờ hoặc bốn buổi 90 phút. Mỗi buổi chỉ nên có một mục tiêu chính và một đầu ra nhỏ. Khi bài thực hành kéo dài hơn dự kiến, ưu tiên hiểu và hoàn thành; lịch roadmap chỉ là khung.

Cloud không cần được chọn bằng cách đoán. Ở Giai đoạn 0, ta có thể ghi "chưa chọn" và dùng lab local. Trước Giai đoạn 3, chọn theo vị trí muốn ứng tuyển, thị trường quanh bạn, tài nguyên học và ngân sách. Với vai trò DevOps Engineer, học sâu một cloud giúp bạn có câu chuyện thực hành rõ hơn học lướt ba cloud.

Ngân sách lab gồm tiền cloud, thời gian và tài nguyên máy cá nhân. Một lab Kubernetes local có thể cần nhiều RAM; nếu máy yếu, dùng bài tập thiết kế hoặc dịch vụ phù hợp hơn. Chất lượng học được đo bằng điều bạn giải thích và thực hiện được, không phải số cluster bạn tạo.

### Checklist trước khi chuyển sang Giai đoạn 1

- Tôi giải thích được vòng đời: mã -> test -> artifact -> triển khai -> quan sát -> cải thiện.
- Tôi biết terminal nào đang dùng và đọc được thư mục hiện tại.
- Tôi đã chọn DevOps Engineer làm hướng tạm thời hoặc ghi rõ hướng khác.
- Tôi có lịch học khả thi và nơi ghi nhật ký.
- Tôi biết không đưa secret vào ghi chú/ảnh chia sẻ.
- Tôi có thể kể bằng lời đường đi của nút Lưu trong ứng dụng ghi chú.

Nếu chưa đạt một dòng, quay lại bài tương ứng. Không cần thuộc các định nghĩa từng chữ.

## Thuật ngữ cần nhớ

- Deployment: đưa một phiên bản ứng dụng vào môi trường chạy.
- CI: tự động kiểm tra và tích hợp thay đổi mã thường xuyên.
- CD: chuẩn bị hoặc tự động đưa phiên bản đã kiểm tra tới môi trường đích, tùy chính sách nhóm.
- Incident: sự kiện làm dịch vụ bị suy giảm hoặc ngừng hoạt động.
- Rollback: quay về trạng thái hoặc phiên bản trước đã biết hoạt động.
- Artifact: sản phẩm build được dùng ở bước sau, như image hoặc gói phần mềm.

## Tiêu chí hoàn thành giai đoạn 0

Bạn có thể giải thích bằng lời của mình đường đi từ mã nguồn đến người dùng, xác định terminal đang dùng, chọn mục tiêu nghề nghiệp tạm thời, ghi thời lượng học và ngân sách lab. Hãy lưu những thông tin đó vào PROGRESS.md. Nếu chưa hiểu một thuật ngữ, ghi lại để hỏi; không đánh dấu hoàn thành chỉ vì đã đọc.

## Tài liệu chính thức

- DORA capabilities: https://dora.dev/capabilities/
- Google SRE Workbook: https://sre.google/workbook/table-of-contents/
- Microsoft WSL install: https://learn.microsoft.com/windows/wsl/install
