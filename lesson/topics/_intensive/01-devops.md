## Học sâu: một thay đổi đi hết vòng đời như thế nào?

Để hiểu DevOps, hãy theo dõi một thay đổi nhỏ: Notes API cần thêm trường `priority` cho ghi chú. Developer sửa code, thêm migration dữ liệu và test. Git ghi được *ai đổi gì*; CI chứng minh một tập điều kiện tối thiểu; registry chứa image có digest; cấu hình triển khai chọn digest; CD đưa cấu hình lên môi trường; observability đo điều người dùng thật gặp. Nếu chỉ nhớ tên Jenkins, Docker và Kubernetes mà không giải thích được chuỗi này, bạn chưa hiểu DevOps.

Viết một bảng cho từng chặng: **đầu vào**, **đầu ra**, **bằng chứng thành công**, **người chịu trách nhiệm**, **cách lùi khi lỗi**. Ví dụ build có đầu vào là commit và dependency đã khóa, đầu ra là image digest; bằng chứng là build log, test và provenance phù hợp. Deploy có đầu vào là digest được phê duyệt và manifest; đầu ra là workload mới; bằng chứng không chỉ `kubectl apply` exit code 0 mà còn rollout, smoke test và tỷ lệ lỗi sau release. Một chặng không có đầu ra định danh được sẽ khiến việc điều tra sự cố khó hơn.

### Năm vòng lặp trong công việc hằng ngày

1. **Thay đổi:** nhận yêu cầu, chia thay đổi nhỏ, review và release. Câu hỏi: bản đang chạy đến từ commit nào?
2. **Phản hồi:** test, scan và staging cho biết lỗi trước production. Câu hỏi: loại lỗi nào chưa được kiểm tra?
3. **Vận hành:** metric/log/trace và alert cho biết dịch vụ thực sự ra sao. Câu hỏi: người dùng bị ảnh hưởng thế nào?
4. **Khôi phục:** rollback, failover, restore và runbook giảm thời gian lỗi. Câu hỏi: thao tác nào đã diễn tập?
5. **Cải tiến:** postmortem và sửa guardrail ngăn lỗi lặp. Câu hỏi: hệ thống đã thay đổi gì sau sự cố?

Không có đội nào tự động hóa mọi thứ ngay. Chọn công việc lặp lại, dễ sai và có thể kiểm chứng kết quả. Một script restart service nhưng không kiểm tra health chỉ tự động hóa động tác; một workflow xác định mục tiêu, ghi log, kiểm tra sau thay đổi và có đường quay lại mới là tự động hóa vận hành có trách nhiệm.

## Bài thực hành trên giấy: thiết kế đường phát hành Notes API

**Đầu vào:** bạn có Git, Python API, SQLite để học local, Docker và một cluster thử nghiệm. **Bài toán:** mỗi merge vào nhánh chính tạo một image; staging cập nhật tự động; production cần phê duyệt; khi tỷ lệ HTTP 5xx tăng sau release, người trực ca xác định được bản lỗi và khôi phục. Không cần cài phần mềm ở bài này.

**Bước 1:** vẽ hai repository hoặc hai phần rõ trong một repository: mã nguồn và cấu hình môi trường. Chỉ ra nơi lưu schema migration, Dockerfile, pipeline, manifest và runbook. Nếu dùng một repo, vẫn phải phân quyền đường production.

**Bước 2:** định nghĩa bốn gate: unit test, integration test với database tạm, render/validate manifest, smoke test sau deploy. Với mỗi gate, ghi lỗi nào nó bắt được và lỗi nào nó không thể bắt. Unit test không phát hiện DNS cloud sai; manifest validation không bảo đảm DB trả lời được.

**Bước 3:** đặt ID xuyên suốt: commit source, image digest, commit deploy, thời điểm sync và incident ID. Trong một ca lỗi, bạn phải nối được request lỗi với bản phát hành. Nếu chỉ ghi `latest`, bạn không thể tái hiện chính xác artifact.

**Bước 4:** mô phỏng tình huống: CI xanh, image triển khai, Notes API trả 500 vì migration chưa chạy. Bạn sẽ tạm dừng release ở đâu? Sửa theo kiểu schema tương thích hay rollback? Bằng chứng nào chứng minh phục hồi? Viết câu trả lời trước khi đọc lời giải dưới đây.

**Lời giải gợi ý:** tạm dừng promotion, xác định bản app và trạng thái schema; giảm tác động bằng rollback chỉ khi schema cũ còn tương thích, nếu không dùng roll-forward/restore theo runbook. Thêm integration test chạy migration trên DB giống cấu hình staging, kiểm tra thứ tự release và smoke test `POST /notes`. Ghi giới hạn: SQLite lab không chứng minh migration MySQL/PostgreSQL production an toàn.

## Các thước đo không được hiểu sai

Deployment frequency và lead time giúp thấy tốc độ đưa thay đổi đến người dùng. Change failure rate và thời gian khôi phục giúp thấy độ ổn định của thay đổi. Nhưng nếu ép đội tăng số lần deploy bằng cách chia commit vô nghĩa, bạn đang làm đẹp số chứ không cải thiện hệ thống. Tương tự, “uptime 99,9%” phải nói rõ cửa sổ đo, endpoint, cách tính và người dùng nào. Một tháng 30 ngày có 43.200 phút; 0,1% tương ứng khoảng 43,2 phút không đạt mục tiêu theo cách tính thời gian đơn giản. SLO thực tế có thể dựa trên tỷ lệ request tốt thay vì số phút.

DevOps Engineer, SRE, Cloud Engineer và Platform Engineer giao nhau ở Linux, mạng, tự động hóa và vận hành. DevOps thường tập trung đường delivery và hạ tầng hỗ trợ phát hành; SRE dùng mục tiêu độ tin cậy và kỹ thuật phần mềm cho vận hành; Cloud Engineer thiên về thiết kế/vận hành dịch vụ cloud; Platform Engineer tạo nền tảng self-service cho đội sản phẩm. JD Việt Nam trộn nhiều phạm vi, nên hãy đọc **trách nhiệm thực tế** thay vì chỉ chức danh. JD yêu cầu VMware, SAN, Ceph, Oracle và Azure chuyên sâu cùng một lúc không có nghĩa người mới phải thành thạo tất cả trước khi ứng tuyển.

## Câu hỏi có lời giải

**Một pipeline xanh có chứng minh release thành công?** Không. Nó chỉ chứng minh các điều kiện đã mã hóa trong pipeline. Cần rollout, smoke test theo nghiệp vụ và quan sát sau release.

**DevOps có phải một bộ công cụ?** Không. Công cụ hiện thực hóa khả năng cộng tác, đo lường, tự động hóa và chịu trách nhiệm đến production. Nếu pipeline tự động nhưng không ai sở hữu phục hồi, vòng đời vẫn đứt.

**Khi nào không nên dùng Kubernetes?** Khi số workload nhỏ, yêu cầu đơn giản và đội chưa đủ năng lực vận hành, VM hoặc dịch vụ managed có thể ít rủi ro hơn. Quyết định dựa trên chi phí vận hành và yêu cầu thực, không dựa trên độ phổ biến của công cụ.

**Bằng chứng học xong:** nộp sơ đồ đường phát hành, bảng năm chặng, bốn gate có giới hạn và một phương án khôi phục migration lỗi. Đọc thêm [DORA capabilities](https://dora.dev/capabilities/) và [Google SRE Workbook](https://sre.google/workbook/).
