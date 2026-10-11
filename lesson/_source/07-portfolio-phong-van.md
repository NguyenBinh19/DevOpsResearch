# Giai đoạn 7 - Chuyên sâu, portfolio và phỏng vấn DevOps

Đây là giai đoạn kết nối kiến thức thành năng lực có thể kiểm chứng. Một dự án không cần dùng mọi công cụ nổi tiếng; nó cần có mục tiêu, cách tái tạo, bằng chứng hoạt động, cách xử lý lỗi và lời giải thích cho các quyết định.

## Bài 1. Chọn nhánh chuyên sâu có chủ đích

Sau các giai đoạn chung, chọn một hoặc hai nhánh. DevOps/Cloud đào sâu IAM, network, multi-environment, IaC và governance. SRE đào sâu SLI/SLO, alerting, incident command, capacity và giảm công việc thủ công lặp lại. Platform đào sâu trải nghiệm của nhóm phát triển, self-service, tiêu chuẩn triển khai và cách đo mức chấp nhận của nền tảng. Delivery/DevSecOps đào sâu test strategy, release safety, quyền pipeline, provenance và auditability.

Một nhánh không xóa kiến thức chung. SRE vẫn cần hiểu deploy; Platform vẫn cần hiểu security; Cloud vẫn cần biết ứng dụng hoạt động ra sao. Hãy chọn theo vấn đề muốn giải và vị trí tuyển dụng thực tế, rồi lấy một hệ thống cụ thể để đi sâu. Nếu không chắc, giữ DevOps Engineer làm nhánh chính và bổ sung SRE ở mức vận hành.

GitOps dùng Git làm nguồn mô tả trạng thái và controller đồng bộ môi trường; progressive delivery kiểm soát phạm vi người dùng khi phát hành; policy as code kiểm tra quy tắc bằng mã. Đây là công cụ/phương pháp có ích khi số môi trường, nhóm hoặc yêu cầu kiểm soát đủ lớn. Trước khi thêm vào portfolio, viết vấn đề hiện tại mà chúng giải quyết và chi phí vận hành mới.

## Bài 2. Thiết kế dự án portfolio xuyên suốt

Đề bài đề xuất: API ghi chú hoặc một dịch vụ web nhỏ có database. Người dùng có thể tạo và đọc dữ liệu; repository có test; CI tạo artifact; ứng dụng chạy trong container; một môi trường local và một môi trường triển khai thử nghiệm có hướng dẫn; IaC mô tả tài nguyên cloud nếu dùng cloud; logs/metrics cho phép điều tra; backup/restore và rollback được diễn tập. Nếu chưa có ngân sách, phần cloud có thể ở dạng thiết kế và lab nhỏ có cleanup rõ; đừng viết trong README rằng hạ tầng đã chạy nếu bạn chưa thực sự chạy.

Chia dự án thành các mốc review được. Mốc 1: app và test chạy local, README nói cách chạy. Mốc 2: Docker/Compose chạy app và database, dữ liệu sống qua restart. Mốc 3: CI kiểm tra và build artifact có version. Mốc 4: deploy, cấu hình và quyền tối thiểu. Mốc 5: dashboard, alert và runbook. Mốc 6: diễn tập lỗi, rollback, backup/restore và viết postmortem. Mỗi mốc có commit, bằng chứng và một quyết định kỹ thuật ngắn.

### Cấu trúc README hữu ích

README nên trả lời: dự án giải quyết gì; kiến trúc bằng sơ đồ; cách chạy local; cách test; cách deploy/rollback; secrets được cung cấp ra sao mà không lộ giá trị; cách xem log/metrics; chi phí dự kiến và cleanup; giới hạn hiện tại. Dùng ảnh minh họa có chú thích nhưng đừng biến ảnh thành bằng chứng duy nhất: người khác cần có thể lặp lại bằng lệnh/hướng dẫn. Nếu chưa làm xong một phần, ghi "chưa triển khai" và kế hoạch thay vì mô tả như đã hoàn thành.

### Bài tập review như người phỏng vấn

Tự mở repo trên một máy hoặc tài khoản mới. Chỉ đọc README, bạn có thể chạy được không? Lệnh nào thất bại? File nào chứa cấu hình mặc định? Nếu xóa một container, data có còn không? Nếu phiên bản mới lỗi, mất bao lâu để quay về? Ghi các câu trả lời cùng kết quả quan sát được và sửa README sau mỗi lần thử.

## Bài 3. Cách trả lời phỏng vấn kỹ thuật

Một câu trả lời mạnh có cấu trúc: xác định mục tiêu và tác động -> nêu giả thuyết -> tìm bằng chứng -> thay đổi nhỏ có rollback -> xác minh -> phòng ngừa lặp lại. Ví dụ câu hỏi "ứng dụng báo 502 sau deploy": kiểm tra thời điểm bắt đầu, phạm vi ảnh hưởng và thay đổi gần nhất; xem proxy/upstream, endpoints, readiness và log; nếu liên quan release mới, cân nhắc rollback để phục hồi; sau đó tìm nguyên nhân gốc. Bạn không cần đoán một nguyên nhân duy nhất từ triệu chứng mơ hồ.

Khi hỏi về công cụ, giải thích bài toán trước cú pháp. "Vì sao dùng Terraform?" có thể trả lời: để mô tả và review thay đổi hạ tầng, tái tạo môi trường, quản lý drift; đồng thời phải bảo vệ state và kiểm tra plan. "Vì sao dùng Kubernetes?" cần nêu nhu cầu điều phối workload và chi phí vận hành; không phải mọi ứng dụng cần cluster.

Phỏng vấn hành vi thường hỏi lần bạn xử lý lỗi, làm việc với nhóm hoặc cân bằng tốc độ và an toàn. Dùng cấu trúc STAR: tình huống, nhiệm vụ, hành động, kết quả. Nếu ví dụ là lab cá nhân, nói rõ đó là lab; không nhận là sự cố sản xuất. Kết quả nên đo được: thời gian phát hiện/khôi phục trong diễn tập, số bước thủ công được giảm, tỷ lệ test qua hoặc tài liệu giúp người khác tái tạo.

### Bộ câu hỏi tự luyện

Linux: service không khởi động, bạn kiểm tra theo thứ tự nào? Networking: DNS đúng nhưng kết nối timeout, bạn thu thập bằng chứng gì? Git/CI: test pass local nhưng fail runner, khác biệt môi trường nào cần xem? Docker: container restart làm mất dữ liệu, vì sao? Cloud: một VM public truy cập được nhưng database không, các lớp quyền/mạng nào cần kiểm tra? Terraform: plan thay database, bạn quyết định ra sao? Kubernetes: Pod Running nhưng Service không có endpoint, tại sao? SRE: một alert liên tục báo CPU 90% nhưng người dùng không bị ảnh hưởng, bạn chỉnh cách cảnh báo ra sao?

Đối với mỗi câu, tự trả lời thành tiếng trong hai phút, rồi bổ sung một ví dụ từ chính repo của mình. Nếu chưa từng làm, tạo lab nhỏ an toàn để lấy bằng chứng. Không học thuộc một "đáp án vàng" vì cấu hình công ty khác nhau.

## Bài 4. Phân biệt sẵn sàng ứng tuyển và trình độ cao

Một portfolio có thể chứng minh bạn có nền tảng và khả năng học. Trình độ cao đòi hỏi quyết định khi yêu cầu mâu thuẫn, sự cố không rõ nguyên nhân, nhiều nhóm cùng phụ thuộc, chi phí thật và thay đổi có hậu quả. Những trải nghiệm này tích lũy qua công việc, dự án mở, cộng tác và diễn tập gần với thực tế. Mục tiêu ngắn hạn của khóa học là giúp bạn giải thích đúng, làm được lab và có bằng chứng để bắt đầu nhận trách nhiệm phù hợp.

Hãy đánh giá tiến bộ bằng năng lực: bạn có thể triển khai lại từ README, lần theo lỗi từ triệu chứng, khôi phục dữ liệu, giải thích chi phí/bảo mật và nêu khi nào nên chọn giải pháp đơn giản hơn không? Số chứng chỉ và tên công cụ trong CV chỉ là phụ. Nếu còn lỗ hổng, quay lại giai đoạn liên quan, làm một lab nhỏ rồi cập nhật portfolio.

## Bài 5. Hồ sơ bằng chứng cho từng năng lực

Một portfolio đáng tin cho người mới nên có bảng năng lực -> bằng chứng. Ví dụ: Git -> lịch sử commit và pull request có mô tả; CI -> workflow và một run thất bại được sửa; Docker -> Dockerfile, Compose và ảnh/log cho dữ liệu sống sau restart; IaC -> file Terraform và bản plan đã xem xét; vận hành -> dashboard, runbook, postmortem lab; bảo mật -> threat model, quyền pipeline và cách quản lý secret. Không cần che giấu lỗi từng gặp: một lỗi được điều tra có phương pháp là bằng chứng học tốt.

Mỗi mục bằng chứng phải trả lời: bạn tự làm phần nào, làm trong môi trường nào, người khác lặp lại ra sao và giới hạn gì. Không dùng từ "production-ready" nếu chưa có test tải, bảo mật, backup, vận hành và bối cảnh yêu cầu. Việc nói rõ "lab local" và "tài nguyên cloud thử nghiệm đã xóa" làm báo cáo chính xác hơn.

### Rubric tự chấm 0-2

Chấm mỗi mục: 0 = chưa có, 1 = có nhưng cần hướng dẫn nhiều, 2 = tự làm và giải thích được. Các mục gồm: chạy/test app; Git/CI; Docker/data persistence; cloud/IAM/network; Terraform plan/state; deploy/rollback; logs/metrics/SLO; backup/restore; security review; README tái tạo. Tổng điểm không phải chứng nhận trình độ; nó chỉ giúp chọn bài cần ôn. Với mục 1 điểm, viết rõ bước nào mình bị kẹt; đó là đầu vào cho buổi học tiếp theo.

## Bài 6. Hai tình huống phỏng vấn có đáp án mẫu

Tình huống 1: "Pipeline xanh, deploy xong người dùng gặp 502." Câu trả lời mẫu: đầu tiên xác nhận phạm vi/tác động và thời điểm; kiểm tra artifact/version vừa deploy; xem proxy hoặc ingress có upstream/endpoint Ready không; đọc log API và health; nếu có bằng chứng bản mới gây lỗi, rollback theo kế hoạch; xác nhận request trở lại thành công; sau đó tìm vì sao test/smoke chưa bắt được. Các nhánh điều tra cụ thể tùy bằng chứng: selector sai, port sai, readiness fail, app crash hoặc kết nối database lỗi. Đừng khẳng định một nguyên nhân khi câu hỏi chưa cung cấp log.

Tình huống 2: "Terraform plan muốn replace database production." Câu trả lời mẫu: không apply; đọc thuộc tính gây replacement và thay đổi từ commit nào; xác định dữ liệu, backup/restore, RPO/RTO và tác động; hỏi có cách thay đổi ít rủi ro hơn hoặc migration tương thích không; review với người sở hữu dữ liệu và quy trình thay đổi; chỉ thực hiện sau khi có kế hoạch, thời điểm và rollback phù hợp. Điều này cho thấy bạn hiểu Terraform chỉ mô tả thao tác, còn trách nhiệm đánh giá hậu quả thuộc nhóm vận hành.

### Bài tập trả lời của chính bạn

Ghi âm hoặc viết câu trả lời 2 phút cho mỗi tình huống trước khi xem mẫu. Sau đó so sánh: bạn có xác định tác động, bằng chứng, hành động giảm ảnh hưởng, xác minh và phòng ngừa chưa? Lặp lại sau một tuần mà không nhìn tài liệu. Nếu không thể giải thích một bước từ chính lab, quay lại làm lab; học thuộc câu mẫu không đủ.

## Bài 7. Bản ghi quyết định kỹ thuật và giới hạn dự án

Viết một ADR ngắn cho một lựa chọn thật của dự án. Cấu trúc: bối cảnh (API ghi chú dùng cho ai, traffic, dữ liệu), quyết định (ví dụ SQLite trong lab local), lý do (không cần server DB, dễ học dữ liệu bền), lựa chọn khác (PostgreSQL), hệ quả (khó phù hợp nhiều tiến trình/máy, backup và truy cập khác), điều kiện xem lại (cần nhiều người dùng/đồng thời hoặc cloud production). Một ADR tốt không cần dài, nhưng phải đủ để người khác hiểu tại sao bạn chọn như vậy ở thời điểm đó.

Làm thêm ADR cho câu hỏi "có cần Kubernetes không?". Với dự án nhỏ, bạn có thể dùng Kubernetes để **học**, đồng thời ghi rõ giải pháp vận hành đơn giản hơn có thể phù hợp cho hệ thống thật. Người phỏng vấn sẽ thấy bạn phân biệt mục tiêu học công cụ với quyết định kiến trúc kinh doanh.

## Bài 8. Kế hoạch phát triển sau portfolio đầu tiên

Sau dự án đầu, đừng nhân bản thêm ba project giống hệt. Chọn ràng buộc mới để buộc mình học sâu: dữ liệu cần phục hồi trong thời gian ngắn hơn; nhiều môi trường; lưu lượng tăng; nhiều service; nhóm khác cần tự triển khai; yêu cầu kiểm toán quyền. Chọn một nhánh chuyên sâu và đo kết quả. Ví dụ nhánh SRE có thể cải thiện alert để giảm nhiễu và diễn tập failover; nhánh Platform có thể xây một template deployment tự phục vụ cho hai ứng dụng khác nhau.

Tìm feedback từ người khác bằng yêu cầu cụ thể: họ có thể chạy repo theo README không, hiểu rủi ro lớn nhất không, có thấy bước nào chứa secret hoặc có thể tốn phí không, runbook có đủ để xử lý lỗi lab không. Ghi feedback và sửa tài liệu/mã. Vòng lặp nhận phản hồi và cải thiện gần với công việc DevOps hơn việc chỉ sưu tập công cụ.

## Cổng năng lực cuối và kế hoạch tiếp tục

Bạn có repo tái tạo được, một demo 5-10 phút, sơ đồ kiến trúc, pipeline, tài liệu vận hành, bằng chứng rollback và restore, một postmortem lab, cùng 10-15 câu hỏi phỏng vấn đã tự trả lời. Sau đó chọn nhánh chuyên sâu và một dự án thứ hai có ràng buộc khác, ví dụ lưu lượng cao hơn, dữ liệu nhạy cảm hơn hoặc nhiều môi trường hơn. Cập nhật PROGRESS.md bằng bằng chứng thật và phản hồi từ người review.

## Tài liệu chính thức

- DORA capabilities: https://dora.dev/capabilities/
- Google SRE Workbook: https://sre.google/workbook/table-of-contents/
- AWS Well-Architected Framework: https://docs.aws.amazon.com/wellarchitected/
- Kubernetes concepts: https://kubernetes.io/docs/concepts/
- Terraform tutorials: https://developer.hashicorp.com/terraform/tutorials
