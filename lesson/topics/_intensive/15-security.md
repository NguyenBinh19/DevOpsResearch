## Threat model bắt đầu từ dữ liệu và ranh giới tin cậy

Với Notes API, tài sản cần bảo vệ là dữ liệu ghi chú, credential DB, quyền deploy và log có thể chứa dữ liệu người dùng. Vẽ đường Internet -> ingress -> API -> DB, thêm CI -> registry -> cluster và operator -> portal. Ở mỗi mũi tên hỏi: ai có thể gửi dữ liệu? ai xác thực? ai có quyền thay cấu hình? dữ liệu được mã hóa/chứng thực ở đoạn nào? log/audit nào giúp phát hiện lạm dụng? STRIDE là khung gợi ý: giả mạo danh tính, sửa dữ liệu, chối bỏ hành động, lộ thông tin, từ chối dịch vụ, nâng quyền. Không cần liệt kê mọi mối đe dọa tưởng tượng; ưu tiên đường có thể khai thác và tác động lớn.

Ví dụ pipeline có token cluster-admin. Một PR sửa pipeline để in token hoặc gọi URL ngoài có thể chiếm cluster nếu job chạy với secret. Biện pháp không chỉ là mask token trong log; cần hạn chế secret chỉ ở protected branch/environment, review thay đổi pipeline, runner tin cậy, token ngắn hạn/identity federation và scope tối thiểu. Tương tự, Kubernetes Secret base64 không phải encryption end-to-end; quyền đọc API, etcd encryption, backup, người có quyền exec vào Pod và log đều là ranh giới phải xét.

## OWASP Top 10 là bản đồ rủi ro, không phải checklist đủ dùng

OWASP Top 10:2025 đã cập nhật các nhóm như Broken Access Control, Security Misconfiguration và Software Supply Chain Failures. Khi học, gắn mỗi nhóm với một ví dụ Notes API. **Broken Access Control:** user A đoán ID note của user B và API chỉ kiểm tra “đã đăng nhập”. **Misconfiguration:** debug endpoint public hoặc CORS mở quá rộng. **Injection:** ghép string SQL từ input. **Supply chain:** dependency/image base chứa mã bị khai thác hoặc pipeline lấy package không đáng tin. Với mỗi ví dụ, ghi phép thử và biện pháp ở code, CI, runtime và monitoring. Đừng kết luận “đã scan là an toàn”; scan chỉ tìm tập lỗi mà scanner biết.

SAST phân tích code không cần app chạy; DAST kiểm thử app đang chạy; SCA theo dõi dependency; image scan quan sát package trong image. CVE có mức nghiêm trọng nhưng cần triage: version thực, package có dùng không, đường tấn công có mở không, exploit đang có, giảm thiểu hiện tại và deadline vá. Không trì hoãn vô hạn bằng “không dùng code path” nếu chưa có bằng chứng. Ghi exception có owner, ngày hết hạn và điều kiện kiểm tra lại.

## Lab threat model trên giấy có lời giải

**Tài liệu đầu vào:** sơ đồ Notes API với HTTPS ingress, API, DB, registry, CI và secret manager. **Bước 1:** chọn ba tài sản: note content, DB credential, deployment permission. **Bước 2:** đánh dấu ba trust boundary: Internet/edge, CI/production, app/DB. **Bước 3:** viết một attack path cho mỗi tài sản. Ví dụ attacker lấy token CI qua job PR -> sửa manifest -> deploy image độc; user A gọi `GET /notes/<id-B>` -> đọc note B; lỗi log in toàn bộ Authorization header -> lộ token qua hệ thống logging. **Bước 4:** cho mỗi path, chọn prevention, detection và recovery. **Bước 5:** ghi residual risk mà biện pháp chưa xử lý.

**Lời giải hướng dẫn:** token CI cần permission hẹp, secret chỉ trên trusted ref, review pipeline, audit và rotation khi lộ. IDOR cần authorization theo object ở API cùng test user A/B; WAF không thay kiểm tra quyền. Log token cần redaction ở source/collector, hạn chế quyền log, retention và quy trình thu hồi token đã lộ. Nếu chỉ nói “dùng Vault” mà không chỉ ra workload nào được lấy secret nào, threat model chưa đủ cụ thể.

## Hardening Linux/container/Kubernetes theo nguyên tắc

Giảm bề mặt tấn công: tắt service không cần, cập nhật có kế hoạch, firewall mặc định hạn chế, chạy app non-root, filesystem chỉ đọc khi hợp lý, drop Linux capabilities, không privileged container, giới hạn network egress/ingress, ServiceAccount quyền tối thiểu, image digest đã duyệt. Mỗi biện pháp phải có test chức năng: app cần ghi tmp ở đâu? DNS có bị NetworkPolicy chặn không? Container non-root có quyền đọc cert/DB file không? Hardening không thể chỉ là bật tất cả option rồi giao outage cho đội vận hành.

Secrets có vòng đời: tạo, cấp, dùng, rotate, thu hồi, audit. Một secret đã vào Git history không được coi là an toàn chỉ vì commit mới xóa nó; cần revoke/rotate. Backup có thể chứa secret cũ nên chính sách truy cập/retention cũng phải phù hợp. Với Key Vault/Vault, identity của workload là điểm quyết định; một app không nên đọc mọi secret trong môi trường.

## Ca ứng phó: phát hiện credential registry trong log CI

Xác định token thuộc principal nào, phạm vi quyền và thời gian log công khai; thu hồi/rotate theo quy trình, kiểm tra audit registry để xem có push/pull lạ, xác định image digest nào bị tác động, tạm dừng promotion nếu cần. Sau đó sửa pipeline để không in token và giảm scope/TTL, kiểm tra branch protection và secret exposure. Chỉ xóa log không thu hồi token là chưa xử lý rủi ro. Ghi incident và thông báo theo chính sách tổ chức; tránh sao chép token vào ticket điều tra.

**Câu hỏi:** khi nào một CVE critical chưa phải việc sửa đầu tiên? Khi không ảnh hưởng asset/runtime thực hoặc đã có mitigating control, trong khi một lỗ hổng bị khai thác trên đường public cần xử lý ngay; quyết định phải có bằng chứng và hạn chót. **Câu hỏi:** TLS có bảo vệ dữ liệu trong DB backup không? Không tự động; TLS bảo vệ đoạn truyền, backup cần mã hóa/quyền riêng. Nguồn: [OWASP Top 10:2025](https://top10.owasp.org/2025/0x00_2025-Introduction/), [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final).
