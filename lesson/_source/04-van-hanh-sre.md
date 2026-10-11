# Giai đoạn 4 - Release, observability và vận hành dịch vụ

Một hệ thống có thể được triển khai thành công nhưng phục vụ người dùng kém. Giai đoạn này dạy cách biết điều gì đang xảy ra, giảm tác động khi lỗi xuất hiện và học từ sự cố để cải thiện lần sau.

## Bài 1. Release là một thay đổi có kiểm soát

Triển khai là hành động đưa phiên bản mới vào môi trường; release là việc cho người dùng sử dụng thay đổi đó. Hai việc có thể tách nhau bằng feature flag hoặc cơ chế điều khiển traffic. Trước mỗi thay đổi, xác định: artifact nào, cấu hình nào, dữ liệu/schema nào, phạm vi tác động, điều kiện thành công và cách quay lại. Một người khác đọc kế hoạch phải biết cách kiểm tra hệ thống sau thay đổi.

Rolling deployment thay dần bản cũ bằng bản mới; blue/green duy trì hai môi trường để chuyển traffic; canary cho một phần nhỏ traffic vào bản mới trước. Mỗi cách đánh đổi tốc độ, tài nguyên, khả năng quan sát và phức tạp. Nếu ứng dụng chỉ có một instance và traffic thấp, một quy trình dừng/ngắn có thể hợp lý hơn xây canary phức tạp. Điều quan trọng là biết rủi ro của lựa chọn.

Rollback ứng dụng không tự động rollback dữ liệu. Nếu bản mới ghi một định dạng database mà bản cũ không hiểu, quay image về sẽ vẫn hỏng. Một chiến lược thường dùng là thay đổi schema theo các bước tương thích: thêm cột/bảng trước, cho mã cũ và mới cùng chạy được, chuyển dữ liệu, sau đó mới bỏ cấu trúc cũ. Bài học đầu tiên: đọc migration cùng với release plan.

### Lab release trên môi trường thử

Điều kiện: ứng dụng mẫu đã có ít nhất hai phiên bản và môi trường local/test. Ghi ID artifact của phiên bản A; deploy và gọi health/API. Deploy B với thay đổi nhỏ; gọi cùng request và ghi thời gian, kết quả. Cố ý cấu hình B sai trong môi trường thử, quan sát lỗi, quay về A; sau đó kiểm tra dữ liệu còn nguyên. Viết checklist gồm điều kiện dừng/rollback, người thực hiện và bằng chứng.

## Bài 2. Logs, metrics và traces trả lời câu hỏi khác nhau

Log là bản ghi một sự kiện: request thất bại, exception, phiên bản khởi động, kết nối database lỗi. Log nên có thời gian, mức độ, tên dịch vụ và mã tương quan request khi phù hợp. Không ghi password/token hay dữ liệu cá nhân không cần thiết. Metrics là số đo theo thời gian: số request, tỷ lệ lỗi, độ trễ, CPU, memory, queue depth. Traces cho thấy một request đi qua nhiều dịch vụ và mất thời gian ở từng đoạn. Không cần cài toàn bộ công cụ ngay; hãy bắt đầu bằng câu hỏi điều tra cụ thể.

Một dashboard tốt giúp trả lời: người dùng có truy cập được không, lỗi tăng từ lúc nào, phần nào thay đổi, hệ thống có đủ tài nguyên không? Tránh dashboard chỉ hiển thị CPU vì CPU thấp không chứng minh API hoạt động. Đo cả tín hiệu người dùng như tỷ lệ request thành công và độ trễ. Phân biệt triệu chứng với nguyên nhân: tỷ lệ 5xx tăng là triệu chứng; nguyên nhân có thể là database pool cạn, cấu hình sai hoặc dependency chậm.

Cardinality là số chuỗi metrics khác nhau do các nhãn tạo ra. Gắn user ID hoặc request ID vào metric có thể tạo quá nhiều chuỗi và tốn tài nguyên. Đặt thông tin chi tiết này trong log/trace, còn metric dùng nhãn có tập giá trị giới hạn như service, endpoint nhóm hoặc status class.

### Lab quan sát

Điều kiện: ứng dụng mẫu có log và endpoint. Tạo 10 request thành công và 2 request lỗi có kiểm soát. Ghi số lượng, status, thời điểm và thông báo log. Tính tỷ lệ thành công trong tập lab, nhưng không gọi con số đó là SLO sản xuất. Thêm một request ID hoặc correlation ID nếu ứng dụng hỗ trợ; lần theo cùng ID qua log. Sau đó cố ý làm database không sẵn sàng trong môi trường thử, quan sát tín hiệu nào xuất hiện trước và tín hiệu nào thiếu.

## Bài 3. SLI, SLO và alert đáng hành động

SLI là chỉ số thể hiện chất lượng dịch vụ theo góc nhìn người dùng, ví dụ tỷ lệ request hợp lệ được trả thành công hoặc độ trễ dưới ngưỡng. SLO là mục tiêu cho SLI trong một khoảng thời gian. Error budget là phần sai lệch được phép khi so với mục tiêu. Ví dụ minh họa: nếu SLO là 99,9% request hợp lệ thành công trong 30 ngày, budget lý thuyết là 0,1% request không đạt; cách tính thực tế phải định nghĩa rõ request nào thuộc mẫu và cách xử lý lưu lượng thấp.

Không phải metric nào cũng nên gọi người trực. Alert tốt chỉ tới vấn đề có tác động đáng kể và có hành động khả thi. Nếu mỗi lần CPU tăng là một cuộc gọi nhưng dịch vụ vẫn ổn, nhóm sẽ mệt và bỏ qua cảnh báo quan trọng. Với hệ thống thực, cảnh báo có thể dựa trên tốc độ đốt error budget; cần thử ngưỡng và giảm nhiễu theo dữ liệu thật.

### Bài tập định nghĩa SLO

Cho API ghi chú, hãy viết: ai là người dùng, request nào hợp lệ, "thành công" là status nào, thời gian đo là bao lâu và dữ liệu lấy từ đâu. Sau đó nêu hai giới hạn của chỉ số: có thể bỏ sót trải nghiệm nào? Nếu database không có request trong 10 phút, liệu 100% thành công có chứng minh dịch vụ tốt không? Đây là bài tập tư duy trước khi chọn Prometheus hoặc công cụ khác.

## Bài 4. Incident, runbook và postmortem

Khi có sự cố, ưu tiên hiểu tác động và khôi phục an toàn. Ghi thời điểm bắt đầu, triệu chứng, phạm vi người dùng, thay đổi gần đây và giả thuyết. Nếu bản deploy mới gây lỗi, rollback có thể nhanh hơn điều tra sâu trong lúc người dùng đang bị ảnh hưởng. Sau khi khôi phục, giữ bằng chứng để tìm nguyên nhân gốc và cải thiện quy trình. Một người phụ trách điều phối có thể giúp tránh nhiều người cùng đổi cấu hình không ghi nhận.

Runbook là hướng dẫn thao tác cho tình huống lặp lại: xác minh triệu chứng, nguồn dữ liệu, bước giảm tác động, điểm dừng và đường liên hệ. Postmortem là tài liệu học từ sự cố: timeline, tác động, yếu tố góp phần, điều đã hiệu quả, điều cần cải thiện và người theo dõi hành động. Mục tiêu là sửa hệ thống và quy trình, không quy lỗi cá nhân.

Backup phải được thử restore trong môi trường an toàn. RPO là lượng dữ liệu tối đa chấp nhận mất (tính theo thời gian); RTO là thời gian mục tiêu để dịch vụ hồi phục. Hai mục tiêu này chi phối tần suất backup và kiến trúc. "Có backup" mà không biết restore mất bao lâu chưa đủ để cam kết phục hồi.

### Diễn tập sự cố

Trong môi trường thử, làm ứng dụng trả lỗi bằng cấu hình sai. Ghi phút phát hiện, tín hiệu quan sát, giả thuyết, hành động giảm ảnh hưởng, thời điểm khôi phục. Viết postmortem một trang. Không diễn tập trên hệ thống có người dùng thật khi chưa có kế hoạch và quyền phù hợp.

## Bài 5. Tính SLI và error budget bằng ví dụ cụ thể

Giả sử trong 30 ngày API nhận 100.000 request hợp lệ. Có 99.850 request được trả thành công theo định nghĩa nhóm đã thống nhất. Availability SLI = 99.850 / 100.000 = 99,85%. Nếu SLO là 99,9%, error budget cho 100.000 request là 100 request không đạt; thực tế có 150 request không đạt, tức đã vượt budget 50. Trong dịch vụ thật, số request thay đổi liên tục nên hệ thống tính theo cửa sổ thời gian và quy tắc lọc rõ ràng. Ví dụ này chỉ giúp hiểu phép tính.

Định nghĩa "thành công" cần thận trọng. Một HTTP 200 có thể trả dữ liệu sai; một HTTP 404 do người dùng yêu cầu ID không tồn tại có thể là hành vi đúng, không nên tính là lỗi hệ thống. Nếu client hủy request, có tính vào mẫu không? Nếu chỉ đo từ server, lỗi DNS trước khi tới server sẽ không xuất hiện. Hãy ghi phạm vi chỉ số và giới hạn của nguồn dữ liệu.

Latency SLI có thể là tỷ lệ request dưới một ngưỡng thay vì chỉ lấy trung bình. Ví dụ 99 request nhanh và 1 request rất chậm có thể tạo trung bình trông ổn nhưng vẫn có người dùng trải nghiệm kém. Tập nhìn phân bố, percentile và số lượng mẫu; percentile trên ít request có thể dao động mạnh. Đừng đặt mục tiêu bằng con số tùy hứng: cần nhu cầu người dùng và dữ liệu thực tế.

### Bài tập tính và diễn giải

Trong 10.000 request, có 9.990 request được xem là thành công. Nếu SLO là 99,95%, budget là 5 lỗi; thực tế có 10 lỗi, vượt budget 5. Hãy tự tính trước khi đọc câu giải. Nếu cả 10 lỗi xảy ra trong một phút, trải nghiệm người dùng khác với 10 lỗi rải đều; vì vậy alert còn cần xem tốc độ lỗi, không chỉ tổng tháng.

## Bài 6. Viết runbook cho một lỗi cụ thể

Ví dụ: sau deploy, tỷ lệ HTTP 5xx của API tăng. Runbook nên bắt đầu bằng xác nhận ảnh hưởng: dashboard nào, bao nhiêu request, môi trường nào, bắt đầu từ lúc nào. Sau đó kiểm tra phiên bản vừa deploy, log lỗi, health/readiness, kết nối database và dependency. Nếu lỗi gắn chặt với bản mới, ghi điều kiện rollback và cách kiểm tra sau rollback. Nếu không, tránh đổ lỗi cho deploy chỉ vì chúng gần nhau về thời gian.

Runbook cần có "điểm dừng": khi nào không tự thử tiếp và phải báo người có quyền/kinh nghiệm hơn. Ví dụ dữ liệu có nguy cơ hỏng, cần chạy migration ngược, hoặc chỉ số không hồi phục sau rollback. Nó cũng cần ghi các lệnh là chỉ đọc hay thay đổi, môi trường nào được phép chạy và cách lưu bằng chứng. Runbook cũ có thể nguy hiểm; trước khi dùng trong production, xác nhận phiên bản và quyền hiện tại.

### Mẫu runbook rút gọn

```text
Trieu chung: 5xx vuot nguong sau release
Xac nhan: thoi gian bat dau, service, moi truong, pham vi nguoi dung
Thu thap: version, release event, logs, readiness, database connectivity
Giam tac dong: rollback neu bang chung cho thay version moi gay loi
Xac minh: smoke request, 5xx trend, latency, data integrity
Dung va bao: neu can can thiep du lieu hoac rollback khong phuc hoi
Sau su co: timeline, root cause, action co owner va han xem lai
```

## Bài 7. Phân biệt backup, restore và disaster recovery

Backup là bản dữ liệu; restore là thao tác đưa dữ liệu từ bản đó trở lại một hệ thống có thể dùng được. Disaster recovery là kế hoạch rộng hơn: người, quyền, hạ tầng, ứng dụng, dữ liệu, DNS và kiểm tra. Trong bài lab, hãy đo thời gian khôi phục cả API chứ không chỉ thời gian copy file database. Nếu file đã được phục hồi nhưng API vẫn dùng sai đường dẫn, người dùng chưa nhận được dịch vụ.

Chọn một sự cố giả: máy chạy ứng dụng mất hoàn toàn. Liệt kê thứ cần tái tạo theo thứ tự: môi trường, cấu hình/secret, artifact ứng dụng, database, route/DNS, kiểm tra. Xác định phần nào có trong Git/IaC, phần nào được backup, phần nào đang nằm trong trí nhớ một người. Chỗ cuối là điểm yếu cần ghi lại. Lặp diễn tập với dữ liệu giả cho tới khi tài liệu đủ để người khác thực hiện.

## Bài 8. Từ log thô đến một cuộc điều tra có giả thuyết

Giả sử 09:15 có release mới. Từ 09:17, 5xx tăng từ gần 0 lên 8%, trong khi GET /health vẫn trả 200. Log cho thấy `sqlite3.OperationalError: unable to open database file` ở request POST /notes. Dữ kiện này gợi ý đường ghi dữ liệu lỗi, không phải toàn bộ HTTP server chết. Các giả thuyết hợp lý: thư mục DB không tồn tại, volume chưa mount, quyền thư mục sai hoặc biến `NOTES_DB` đổi. Bạn có thể kiểm tra cấu hình và quyền trong môi trường test, đối chiếu thay đổi release; nếu ảnh hưởng người dùng thật và rollback an toàn, phục hồi trước rồi tìm nguyên nhân chi tiết sau.

Một log tốt có thời gian, service, version, request ID và lỗi đủ rõ. Nhưng log thô có thể quá nhiều. Metric `http_requests_total{status_class="5xx"}` cho xu hướng; trace của request cho biết đoạn nào chậm hoặc lỗi. Mỗi công cụ trả lời một câu hỏi. Tập viết giả thuyết trước khi mở dashboard: "Nếu volume mount sai, log POST sẽ báo lỗi file và GET /health vẫn hoạt động". Sau đó tìm bằng chứng ủng hộ hoặc bác bỏ.

### Bài tập diễn giải dashboard

Bạn thấy latency p95 tăng nhưng 5xx vẫn thấp. Những giả thuyết đầu tiên có thể là database chậm, hàng đợi dài hoặc dependency ngoài chậm. CPU cao có thể liên quan nhưng không đủ để kết luận. Hãy chọn ba phép đo tiếp theo và nêu vì sao: thời gian truy vấn DB, số kết nối chờ, độ trễ theo endpoint hoặc trace của request chậm. Nếu latency chỉ tăng ở POST, phạm vi điều tra thu hẹp hơn toàn ứng dụng.

## Bài 9. Phòng ngừa alert mệt mỏi và vận hành có trách nhiệm

Một alert nên có người nhận, mức ưu tiên, điều kiện, hành động đầu tiên và cách tắt sau khi vấn đề đã được xử lý. Nếu alert đêm nào cũng nổ vì CPU tăng ngắn nhưng không có tác động, nó làm nhóm mất niềm tin. Trước khi nâng ngưỡng bừa bãi, xem service có thực sự bị ảnh hưởng không, metric có nhiễu không, khoảng đo có phù hợp không và alert có nên chuyển thành dashboard/ticket thay vì gọi người trực.

Trong postmortem, hành động cải thiện phải kiểm tra được. "Cẩn thận hơn" không phải hành động kỹ thuật rõ. "Thêm test kiểm tra quyền ghi volume trong staging trước release", "ghi version vào log khởi động" hoặc "diễn tập restore mỗi quý" là những việc có owner và bằng chứng. Ưu tiên hành động giảm khả năng lặp hoặc giảm thời gian phát hiện/khôi phục, cân đối với chi phí.

### Mini review cuối giai đoạn

Mở ứng dụng mẫu và tự trả lời bằng bằng chứng: bản nào đang chạy; request nào lỗi; log/metric nào cho thấy; nếu database file mất thì restore thế nào; nếu bản deploy mới lỗi thì rollback ra sao; nếu cảnh báo nổ nhưng người dùng vẫn ổn thì bạn làm gì. Nếu chỉ trả lời bằng lý thuyết, làm thêm một diễn tập local rồi ghi kết quả.

## Cổng năng lực và câu hỏi phỏng vấn

Bạn có thể xác định phiên bản đang chạy, thực hiện rollback có kiểm tra, phân biệt log/metric/trace, viết SLI/SLO đơn giản, tạo cảnh báo có hành động, diễn tập incident và restore dữ liệu thử. Tự trả lời: Khi 5xx tăng nhưng CPU bình thường, bạn kiểm tra gì? Khi alert nổ liên tục nhưng không có tác động, bạn sửa gì? Vì sao rollback image có thể không đủ?

## Tài liệu chính thức

- Google SRE Workbook - Monitoring: https://sre.google/workbook/monitoring/
- Google SRE Workbook - Alerting on SLOs: https://sre.google/workbook/alerting-on-slos/
- OpenTelemetry docs: https://opentelemetry.io/docs/
- DORA monitoring and observability: https://dora.dev/capabilities/monitoring-and-observability/
