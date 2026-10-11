## Đọc template bằng một ví dụ nhỏ

Giả sử `values.yaml` có `service.port: 8080`, `service.targetPort: 8000` và Deployment container nghe 8000. Service template lấy `{{ .Values.service.port }}` và `{{ .Values.service.targetPort }}`; sau render, client trong cluster gọi Service:8080, proxy tới Pod:8000. Nếu người sửa values đặt `targetPort: 8080` nhưng process vẫn nghe 8000, manifest hoàn toàn hợp lệ và Pod Ready có thể vẫn đúng nếu probe gọi cổng khác; request qua Service thất bại. Vì thế khi review chart, đọc một **đường request trọn vẹn**: Ingress backend port -> Service port -> targetPort -> process listen, cộng selectors/labels. Một chart chỉ “lint xanh” không chứng minh đường này.

Trước khi deploy, in manifest cho staging và production rồi so: image digest, replicas, resources, probes, env, Secret refs, Service/Ingress, RBAC, PVC. Nếu chỉ khác `replicaCount`, diff cần nhỏ và giải thích được. Nếu production values vô tình đổi `service.type` thành LoadBalancer, diff có thể tạo exposure/cost mới. Review **rendered manifest** làm lộ tác động thật của values, không chỉ file values vài dòng. Đối với chart bên thứ ba, đọc changelog và diff templates khi nâng version; default values mới có thể đổi hành vi dù file override của bạn không đổi.

## Chart dependency và supply chain

Một chart có thể phụ thuộc subchart DB/Redis. Với production, hỏi có nên để chart ứng dụng tự cài DB stateful hay dùng DB được đội dữ liệu quản lý. Subchart tiện lab nhưng có thể kéo storage/backup/upgrade vào vòng đời app release ngoài ý muốn. `Chart.lock` và version constraint giúp tái hiện dependency theo cơ chế Helm; vẫn cần kiểm soát repository nguồn và provenance/integrity nếu tổ chức yêu cầu. Một chart public có thể đổi template hoặc image reference giữa hai lần kéo; pin version và review artifact.

**Bài tập:** chart Notes API bật DB subchart ở staging, production dùng DB managed. Viết hai values files, render và kiểm tra production không tạo StatefulSet/PVC ngoài ý muốn, app env trỏ DB production qua Secret reference, network policy chỉ cho đường cần thiết. Nếu chart không hỗ trợ rõ hai mode, quyết định sửa chart/đơn giản hóa thay vì chồng hàng loạt `--set` khó hiểu.

## Release history có giới hạn

Helm lưu lịch sử release để xem revision và rollback theo cơ chế phiên bản đang dùng. Lịch sử này không phải backup mọi thứ: PVC data, external DB, secret manager, image registry nằm ngoài chart. Nếu registry xóa image cũ, rollback manifest có thể kẹt `ImagePullBackOff`. Nếu DB migration đã xóa cột, app cũ rollback có thể crash. Kế hoạch release phải giữ artifact cần thiết, migration tương thích và kiểm tra sau rollback. Đặt retention lịch sử không quá thấp để còn truy vết, nhưng cũng xét storage/quyền đọc manifest có thể chứa dữ liệu nhạy cảm.

### Ca có lời giải: `helm upgrade` thành công, Argo báo OutOfSync

Nếu Argo quản lý cùng app từ Git, một upgrade thủ công đổi live state ngoài Git. Argo so và báo drift; self-heal có thể đưa về Git. Không “sửa” bằng cách tắt Argo lâu dài. Xác định owner, đưa thay đổi chart/values vào Git, review, để Argo sync; nếu hotfix khẩn cấp, ghi incident và hợp thức hóa Git sau. Nếu release thật do Helm CLI quản lý chứ không qua Argo, kiểm tra vì sao Application Argo lại theo dõi cùng resource và loại bỏ ownership trùng.

### Ca có lời giải: một giá trị boolean bị parse sai

Bạn muốn `feature.enabled=false` nhưng dùng `--set feature.enabled="false"` hoặc file values với kiểu string ở nơi chart kỳ vọng boolean. Tùy cách parse và template, điều kiện có thể vẫn bật hoặc render sai. Dùng file YAML có kiểu rõ, schema chart nếu có, `helm template` và kiểm tra resource sinh ra. Trong phỏng vấn, nói “kiểu dữ liệu values” và output manifest, không chỉ “Helm bug”.

Bạn đạt phần này khi có thể cầm một chart chưa thấy, render hai môi trường, giải thích một diff có tác động bảo mật, và nói vì sao rollback chart chưa đủ cho dữ liệu. Đọc [Helm template guide](https://docs.helm.sh/docs/chart_template_guide/) theo phiên bản của bạn.

**Thử thách cuối:** tạo một thay đổi values chỉ định `resources.requests.memory` thấp hơn mức app thực dùng. Trước khi apply, dự đoán scheduler sẽ dễ đặt Pod hơn nhưng runtime có thể OOM nếu limit cũng thấp hoặc node quá tải; render manifest để biết requests và limits thực. Nếu rollout kẹt, đọc Pod Events/status chứ không quy mọi lỗi cho Helm. Helm tạo YAML; Kubernetes quyết định schedule/run; ứng dụng quyết định phục vụ nghiệp vụ. Ba tầng có bằng chứng khác nhau.
