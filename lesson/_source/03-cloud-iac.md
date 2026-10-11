# Giai đoạn 3 - Cloud, IAM và Infrastructure as Code

Cloud là cách thuê và quản lý tài nguyên qua API: máy tính, mạng, lưu trữ, database và dịch vụ quản lý. Nhà cung cấp cung cấp khả năng và giới hạn; bạn vẫn phải quyết định kiến trúc, quyền, dữ liệu, chi phí và cách vận hành. Bài giảng dùng khái niệm chung, sau đó bạn chọn một cloud để thực hành sâu.

## Bài 1. Một ứng dụng chạy trên cloud gồm gì?

Hãy vẽ đường đi: người dùng -> DNS -> điểm vào public/load balancer -> ứng dụng -> database. Mỗi thành phần cần vị trí, quyền và đường mạng. Compute có thể là VM, container service hoặc serverless. VM cho quyền kiểm soát hệ điều hành nhiều hơn nhưng bạn phải quản lý vá lỗi và tiến trình. Dịch vụ managed giảm một phần công việc vận hành nhưng giới hạn tùy chỉnh và có mô hình giá riêng. Không có lựa chọn đúng cho mọi hệ thống.

Region là khu vực địa lý của cloud; zone là vùng tách biệt trong region theo thiết kế nhà cung cấp. Tính sẵn sàng cao đòi hỏi xem lỗi nào cần chịu được: tiến trình, máy, zone, region hay dependency bên ngoài. Hai bản sao ứng dụng cùng nằm trên một máy không giúp khi máy đó hỏng. Ngược lại, nhân bản qua nhiều zone làm tăng chi phí và độ phức tạp; nhu cầu kinh doanh quyết định mức đầu tư.

Storage khác nhau ở cách truy cập và tính chất: object storage phù hợp file/backup; block storage gắn với VM hoặc workload; database managed cung cấp truy vấn và chức năng dữ liệu. Đừng gọi mọi thứ là "ổ đĩa". Dữ liệu cần backup, restore và chính sách lưu giữ; replication không thay thế backup vì lỗi xóa nhầm có thể được nhân bản.

### Ví dụ kiến trúc nhỏ

Ứng dụng ghi chú có một API và database. Giai đoạn đầu có thể chạy API trên VM và database managed hoặc cả hai ở local cho lab. Nếu cần public, đưa API qua HTTPS; database chỉ cho API kết nối và không mở công khai. Lưu cấu hình không bí mật riêng với secret. Ghi log request/error và giới hạn chi phí. Trước khi mở rộng, đo lưu lượng và yêu cầu phục hồi.

### Bài tập giấy trước khi chạm cloud

Vẽ ba hộp compute, database và object storage. Ghi mũi tên kết nối, data nào nhạy cảm, component nào cần public và người dùng nào được phép thay đổi chúng. Giải thích vì sao database không cần public IP chỉ để API đọc/ghi. Bài tập này giúp tránh tạo tài nguyên tốn phí khi kiến trúc chưa rõ.

## Bài 2. IAM, mạng và chi phí

IAM (Identity and Access Management) trả lời ai có thể làm gì với tài nguyên nào, trong điều kiện nào. Identity có thể là người dùng, service account hoặc workload identity. Permission là quyền hành động; role/policy nhóm quyền. Quyền tối thiểu nghĩa là cấp đủ cho công việc hiện tại, rồi mở rộng khi có bằng chứng cần thiết. Tài khoản dùng hằng ngày không nên có quyền quản trị toàn bộ chỉ để chạy một lab.

Mạng cloud thường gồm mạng ảo, subnet, route và bộ lọc truy cập. Subnet chia phạm vi địa chỉ; route quyết định đường đi; firewall/security group quyết định traffic nào được phép. Một dịch vụ không truy cập được có thể do DNS, route, firewall, listener, TLS hoặc lỗi ứng dụng. Hãy chẩn đoán theo lớp thay vì mở tất cả cổng để thử.

Chi phí cloud phụ thuộc thời gian chạy, loại tài nguyên, dung lượng và lưu lượng. Tài nguyên "nhỏ" vẫn có thể phát sinh phí nếu quên xóa. Trước lab, đọc trang giá hiện hành của dịch vụ bạn dùng, đặt ngân sách/cảnh báo khi có, đặt tên tài nguyên dễ tìm và viết checklist cleanup. Không coi cảnh báo ngân sách là giới hạn cứng: nhiều nền tảng chỉ thông báo sau khi chi phí đã phát sinh.

### Lab cloud có kiểm soát

Chỉ làm khi bạn đã chọn nhà cung cấp, tài khoản thử nghiệm và ngân sách. Bắt đầu bằng xem danh sách region, IAM identity hiện tại, service đang hoạt động và công cụ theo dõi chi phí. Tạo một tài nguyên nhỏ nhất cần cho bài học, ghi ID, region, quyền, giá dự kiến; xác minh rồi xóa sau buổi. Không thực hiện lệnh tạo/xóa từ tài liệu chung mà chưa kiểm tra đúng tài khoản và tên tài nguyên. Nếu chưa có tài khoản cloud, dùng sơ đồ và lab local để học khái niệm, rồi thực hành sau.

## Bài 3. Terraform và ý nghĩa của state

Infrastructure as Code (IaC) là mô tả hạ tầng bằng file có thể review và lưu lịch sử. Terraform đọc cấu hình mong muốn, đối chiếu với state và hệ thống thật, rồi tạo một plan các thay đổi dự kiến. `plan` không phải lời bảo đảm tuyệt đối về mọi kết quả thực thi; môi trường có thể thay đổi giữa lúc lập plan và apply. Người thực hiện phải đọc plan, nhất là mục thay thế hoặc xóa.

Một resource là đối tượng Terraform quản lý; provider nói chuyện với API của nền tảng. Variable giúp thay đổi đầu vào; output công bố thông tin cần dùng; module đóng gói một phần cấu hình. Bắt đầu với cấu hình nhỏ trước khi tạo nhiều lớp module. Module phức tạp quá sớm khiến người mới khó nhìn thấy tài nguyên thật được tạo ra.

State lưu ánh xạ giữa resource trong cấu hình và đối tượng thực. State có thể chứa dữ liệu nhạy cảm, nên cần kiểm soát quyền và nơi lưu. Khi nhiều người cùng sửa, locking giúp tránh ghi đè đồng thời. Xóa state file không tương đương xóa hạ tầng; tự ý sửa state có thể khiến Terraform hiểu sai môi trường. Drift là khác biệt do thay đổi ngoài quy trình; phát hiện drift trước khi apply để tránh ghi đè ngoài ý muốn.

### Lab Terraform local trước cloud

Điều kiện: đã cài Terraform và có một provider an toàn cho lab. Chọn hướng dẫn chính thức "Get Started" phù hợp môi trường. Đọc file cấu hình, chạy `terraform init`, `terraform fmt`, `terraform validate`, `terraform plan`. Trước apply, ghi lại số tài nguyên tạo/sửa/xóa và những giá trị chưa biết. Chỉ apply với tài nguyên thử nghiệm mà bạn hiểu cách dọn. Sau đó sửa một thuộc tính, quan sát plan; cuối cùng dùng `terraform destroy` đúng workspace/lab và kiểm tra tài nguyên thực đã biến mất. Đừng commit state hay biến chứa secret.

### Tình huống điều tra

Plan báo "replace" một database. Dừng lại và tìm thuộc tính gây thay thế. Hỏi dữ liệu hiện tại ở đâu, có backup/restore đã thử chưa, tác động downtime là gì và có cách migration khác không. Một câu trả lời tốt trong phỏng vấn không phải "chạy apply" mà là giải thích cách đánh giá tác động và chọn thời điểm/chiến lược an toàn.

## Bài 4. Lab Terraform không tốn phí cloud

Thư mục `lesson/labs/terraform-local` có một `main.tf` dùng resource tích hợp `terraform_data`. Resource này lưu một giá trị trong Terraform state và không tạo tài nguyên cloud. Nhờ đó bạn có thể học vòng lặp init -> plan -> apply -> thay đổi -> destroy trước khi sử dụng tài khoản có tính phí. Đây là lab về mô hình hoạt động của Terraform, chưa phải bài thiết kế hạ tầng thực.

Mở terminal ở thư mục này. `terraform version` cho biết công cụ có sẵn hay chưa. `terraform init` chuẩn bị thư mục làm việc. `terraform fmt -check` kiểm tra định dạng; `terraform validate` kiểm tra cú pháp và một số quy tắc cấu hình. `terraform plan` cho xem dự kiến một `terraform_data.label` sẽ được tạo. Đọc ba dòng quan trọng: tên resource, giá trị input và tổng số create/change/destroy. Chỉ sau khi hiểu plan, chạy `terraform apply` trong lab này và xác nhận. Dùng `terraform output resource_label` để xem kết quả mong đợi `notes-lab`.

Sửa default của variable từ `lab` thành `demo`, chạy plan lại. Trước khi xem output, dự đoán Terraform sẽ tạo mới, cập nhật hay thay resource. Đọc plan thực tế và giải thích tại sao. Quay lại `lab` nếu muốn, rồi chạy `terraform destroy` trong đúng thư mục lab; plan phải cho biết đối tượng state nào sẽ bị xóa. Vì lab dùng `terraform_data`, thao tác destroy chỉ bỏ state tương ứng, không xóa máy/cloud. Đừng suy rộng điều này sang các resource cloud khác.

State file local được tạo sau apply. Dùng `terraform state list` để xem địa chỉ resource; có thể dùng `terraform show` để đọc state theo cách công cụ hỗ trợ. Không chỉnh state bằng editor. Nếu thấy file state trong `git status`, thêm quy tắc ignore phù hợp trước khi commit. State của project thật có thể chứa dữ liệu nhạy cảm và phải được lưu/khóa theo chính sách nhóm.

### Nếu lab lỗi

Nếu `terraform` không được nhận diện, công cụ chưa cài hoặc chưa nằm trong PATH; dùng hướng dẫn cài chính thức cho hệ điều hành, rồi mở terminal mới. Nếu `init` lỗi tải provider, kiểm tra kết nối mạng và proxy; lab tích hợp có thể không cần provider ngoài nhưng Terraform vẫn cần chuẩn bị môi trường. Nếu `plan` báo lock, xem có tiến trình Terraform khác đang chạy không; không tự xóa lock của team. Với lab cá nhân, đọc thông báo để hiểu trường hợp cụ thể.

## Bài 5. Tập quyết định kiến trúc với bốn câu hỏi

Trước khi chọn dịch vụ cloud, viết yêu cầu về traffic, dữ liệu, độ sẵn sàng và ngân sách. Ví dụ API ghi chú phục vụ nhóm 20 người, dữ liệu không quá lớn, chấp nhận vài phút ngừng dịch vụ trong lab và ngân sách thấp. Từ đó, một VM hoặc dịch vụ container managed cùng database managed nhỏ có thể là hai phương án đáng so sánh. Kubernetes nhiều node thường vượt nhu cầu và làm lab khó dọn hơn. Khi quy mô, yêu cầu uptime hoặc số nhóm tăng, xem lại quyết định.

Đối với mỗi phương án, trả lời: ai vá hệ điều hành và runtime; data ở đâu và backup thế nào; ai được phép deploy; khi một zone lỗi thì điều gì xảy ra; nếu quên tắt tài nguyên thì chi phí ra sao. Đây là cách dùng framework kiến trúc: chuyển tiêu chí chung thành câu hỏi cụ thể cho workload. Không có thiết kế "best practice" nếu chưa nói rõ bối cảnh.

### Bài tập IAM và mạng có đáp án gợi ý

Ứng dụng cần đọc/ghi một database, CI cần triển khai image, còn người học cần xem log. Tách thành ba identity. App identity chỉ có quyền cần để kết nối database; CI identity có quyền deploy vào môi trường thử và đọc artifact cần thiết; learner identity đọc log, không cần quyền xóa database. Nếu tất cả cùng dùng một admin credential, khi một chỗ lộ thì phạm vi thiệt hại rất lớn.

Giả sử API có public endpoint nhưng database chỉ cho kết nối từ subnet/private network của ứng dụng. Khi API trả 500 vì không kết nối được DB, đừng mở database ra internet. Hãy kiểm tra địa chỉ cấu hình, DNS/private name, route, firewall ở cả hai đầu, credential và log database. Khi bạn xác định được lớp nào chặn kết nối, thay đổi đúng lớp đó rồi kiểm tra lại. Đường mạng thông không chứng minh credential hợp lệ.

## Bài 6. Chi phí và cleanup là một phần của lab

Trước khi tạo tài nguyên, viết bảng: tên tài nguyên, region, dịch vụ, đơn vị tính phí, thời gian dự kiến, mức cảnh báo và lệnh/quy trình xóa. Sau buổi học, đối chiếu danh sách tài nguyên thực với bảng. Một VM đã tắt có thể vẫn còn storage; một load balancer, public IP hoặc managed database có thể tiếp tục tính phí tùy nhà cung cấp. Vì giá thay đổi, luôn dùng trang giá hiện hành của dịch vụ và vùng bạn chọn. Cảnh báo ngân sách giúp phát hiện, nhưng không nhất thiết tự chặn tiêu dùng.

Nếu Terraform quản lý tài nguyên, `destroy` cần được xem như một thay đổi có tác động: nhìn plan, kiểm tra tài khoản/region/workspace, xác nhận tên tài nguyên và dữ liệu. Nếu tài nguyên được tạo thủ công ngoài Terraform, destroy không biết để xóa. Sau thao tác, kiểm tra console/API và trang billing; đừng chỉ tin vào dòng "complete" của một công cụ.

## Bài 7. Đọc một thiết kế network cloud

Giả sử mạng ảo dùng dải `10.20.0.0/16`, trong đó subnet public cho load balancer và subnet private cho ứng dụng/database. Ký hiệu `/16` cho biết số bit đầu cố định của địa chỉ; subnet như `10.20.1.0/24` và `10.20.2.0/24` là các phần nhỏ hơn. Bạn chưa cần tính nhẩm mọi địa chỉ, nhưng phải hiểu rằng hai subnet có phạm vi địa chỉ và route khác nhau. "Public" không chỉ do tên subnet: cần xét route tới internet, public IP, bộ lọc mạng và dịch vụ có đang lắng nghe hay không.

Khi người dùng truy cập `https://notes.example`, DNS trỏ tới điểm vào. TLS có thể kết thúc ở load balancer hoặc proxy theo thiết kế. Điểm vào chuyển tới API trong subnet private; API nói chuyện database qua đường private. Nếu API lỗi kết nối DB, theo lớp: host/port cấu hình; DNS nội bộ; route và firewall; DB đang chạy; xác thực; giới hạn kết nối. Không mở port DB cho `0.0.0.0/0` chỉ để thử; nó làm tăng phạm vi tấn công mà không chứng minh nguyên nhân.

### Bài tập CIDR và luồng traffic

Vẽ hai subnet `10.20.1.0/24` và `10.20.2.0/24`, đặt API ở subnet thứ nhất, DB ở subnet thứ hai. Ghi rule ý tưởng: chỉ API được kết nối tới cổng DB; người dùng chỉ tới cổng HTTPS của điểm vào. Sau đó nêu ít nhất hai lý do kết nối vẫn có thể lỗi dù rule này đúng: DB không lắng nghe, credential sai, DNS sai hoặc route thiếu. Bài tập muốn bạn tách **network reachability** khỏi **authentication**.

## Bài 8. State, drift và thay đổi ngoài quy trình

Terraform state là trí nhớ của Terraform về các đối tượng mà nó quản lý. Nếu ai đó sửa tài nguyên qua console, cấu hình trong Git chưa thay nhưng hệ thống thật đã khác. Lần plan sau có thể cho thấy Terraform muốn đưa hệ thống về trạng thái cấu hình; đó là một dấu hiệu drift. Tuy nhiên, không phải mọi thay đổi hiển thị trong plan đều do người sửa tay: provider có giá trị tính toán, API có mặc định và phiên bản provider có thể thay đổi. Đọc diff cụ thể trước khi kết luận.

Trong lab `terraform_data`, đổi giá trị `environment` rồi chạy plan để thấy khác biệt có chủ ý. Quay lại file cũ nhưng chưa apply và quan sát plan đổi. Bài này mô phỏng vòng lặp cấu hình/state. Với cloud thật, còn một nguồn trạng thái nữa là tài nguyên trong API cloud. Đó là lý do cần quản lý quyền thay đổi thủ công và review plan thường xuyên.

Không đưa `terraform.tfstate` lên Git. Nếu hai người cùng apply vào cùng môi trường bằng hai bản state độc lập, mỗi người có thể hiểu sai quyền sở hữu tài nguyên. Remote state với locking phù hợp giúp nhóm dùng chung trạng thái, nhưng quyền đọc state cũng cần hạn chế vì secret có thể xuất hiện trong đó. Đánh dấu output `sensitive` giúp giảm lộ trên CLI nhưng không thay thế bảo vệ state.

## Bài 9. Review plan như một thay đổi sản xuất

Một plan cần được đọc theo bốn tầng. Tầng 1: đúng account, region, workspace và commit không? Tầng 2: số resource tạo/sửa/xóa/thay thế là bao nhiêu? Tầng 3: thuộc tính nào gây tác động, đặc biệt địa chỉ public, IAM permission, database, storage và backup? Tầng 4: nếu apply thất bại giữa chừng hoặc kết quả khác dự kiến, cách phát hiện và phục hồi là gì? Bài lab có thể bỏ qua một số bước vì không tạo cloud, nhưng thói quen đọc plan cần bắt đầu từ đây.

Giả sử plan thêm một security rule cho phép `0.0.0.0/0` tới cổng database. Tên resource có thể trông hợp lệ, nhưng nội dung rule nguy hiểm. Người review cần hiểu đường traffic dự kiến và yêu cầu sửa về nguồn hẹp hơn. Giả sử plan xóa một storage bucket chứa backup; dừng và kiểm tra dữ liệu, retention, owner, mục đích. Không đo chất lượng IaC bằng việc `terraform apply` kết thúc thành công; đo bằng kết quả hệ thống và rủi ro đã kiểm soát.

## Cổng năng lực và câu hỏi phỏng vấn

Bạn giải thích được đường đi của request qua cloud, xác định thành phần public/private, phân biệt identity với permission, ước tính và dọn chi phí lab, đọc plan Terraform và mô tả vai trò của state. Hãy thử trả lời: replication có thay backup không? Vì sao một app không truy cập được dù VM đang chạy? Vì sao remote state cần quyền kiểm soát? Khi nào managed service đáng chọn hơn tự vận hành trên VM?

## Tài liệu chính thức

- AWS Well-Architected Framework: https://docs.aws.amazon.com/wellarchitected/
- Google Cloud Well-Architected Framework: https://docs.cloud.google.com/architecture/framework
- Terraform tutorials: https://developer.hashicorp.com/terraform/tutorials
- Terraform state: https://developer.hashicorp.com/terraform/language/state
