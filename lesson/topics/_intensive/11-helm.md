## Tư duy đúng: chart là chương trình tạo manifest

Helm chart không phải “một file YAML lớn”. Chart chứa `Chart.yaml` metadata, `values.yaml` mặc định, thư mục `templates/` có Go templates và có thể có dependencies. Khi render, Helm kết hợp chart, values của môi trường, CLI overrides và khả năng cluster để tạo manifest Kubernetes. Kubernetes chỉ thấy **manifest cuối cùng**; nếu Pod lỗi, phải truy từ values qua template đến YAML đã áp. Một values key có tên đẹp không bảo đảm template thực sự dùng nó. Đọc rendered output là bước quan trọng hơn học thuộc `helm install`.

Ví dụ `replicaCount: 2` trong values và template dùng `{{ .Values.replicaCount }}` cho Deployment. Nếu file production đặt `replicas: 3` thay vì `replicaCount: 3`, Helm có thể vẫn render 2 mà không báo lỗi nếu chart không có schema/validation. Vì vậy review values cần kèm `helm template` hoặc `helm lint` và kiểm tra output theo điều kiện dự kiến. `values.schema.json` có thể bắt một số lỗi kiểu/dải giá trị, nhưng không thay test logic và Kubernetes validation.

### Thứ tự ghi đè và ba số phiên bản

Chart có **chart version** (phiên bản gói), **appVersion** (metadata mô tả ứng dụng) và image tag/digest thực trong template. Chúng không tự đồng bộ. Một chart version đổi vì sửa probe mà app image không đổi; một image đổi mà chart version có thể chưa đổi trong chart nội bộ. Với release có thể tái hiện, ghi chart source/version, values cụ thể, image digest và revision Git. Nhiều file `-f` được kết hợp theo thứ tự, file sau có thể ghi đè file trước; CLI `--set` cũng có thể làm cấu hình khác Git. Trong production nên giảm tham số thao tác tay khó audit.

## Lab đọc chart Notes API một cách có bằng chứng

**Điều kiện:** Helm CLI và kubectl đã cài; dùng chart trong `lesson/labs/helm-notes`, không dùng cluster production. Chạy `helm version` và ghi major version vì Helm 4 đã xuất hiện trong tài liệu hiện hành; tra cú pháp đúng phiên bản CLI của bạn. Trước khi render, dự đoán số Deployment, Service, replica, image, port và probe mà chart tạo. Chạy `helm lint lesson/labs/helm-notes` và `helm template notes-lab lesson/labs/helm-notes -n devops-lab` rồi lưu output để đọc. **Kết quả dự kiến:** manifest Kubernetes có các giá trị từ chart; lint có thể không chứng minh image tồn tại hoặc Pod Ready.

Tạo một file values lab riêng đổi replica từ 1 sang 2 và image/tag hợp lệ theo chart. Render lại với `-f <file-values-lab>`; so diff đầu ra, chỉ rõ trường nào đổi. Nếu chart dùng một key khác dự đoán, quay lại template/values và giải thích. Thử cố ý viết sai tên key trong **file lab**, render lại: nếu output không đổi, đây là ví dụ silent misconfiguration. Đừng áp lên cluster trước khi nhìn ra sự khác biệt. Nếu chart có schema chặn lỗi, ghi thông báo và giải thích lớp bảo vệ đó.

Khi đã có cluster kind riêng và context đúng, `helm install notes-lab lesson/labs/helm-notes -n devops-lab --create-namespace` theo cú pháp phiên bản của bạn. Xem `helm status`, `helm get manifest`, `kubectl get deploy,svc,pods -n devops-lab`, `kubectl rollout status`. Sau một thay đổi values, dùng `helm upgrade`, đọc `helm history` và quan sát resource diff. Dọn bằng `helm uninstall notes-lab -n devops-lab` rồi xác nhận resource còn hay không; namespace/PVC/CRD có thể có vòng đời riêng. Không giả định uninstall là xóa dữ liệu hoàn toàn.

## Template logic: dễ tiết kiệm sao chép, cũng dễ giấu lỗi

Go template có `if`, `range`, `include`, helpers và pipeline. Helper cho labels/tên thống nhất là tốt, nhưng lồng nhiều điều kiện khó kiểm tra mọi tổ hợp. Một chart có 12 boolean có thể tạo nhiều biến thể; không phải biến thể nào cũng được CI render. Định nghĩa cấu hình được hỗ trợ, test ít nhất values mặc định và từng môi trường thật. Nếu một tùy chọn tắt Service nhưng Ingress vẫn trỏ vào Service đó, render có thể hợp lệ về cú pháp nhưng app không phục vụ. Một chart tốt giảm bất ngờ, không tối đa hóa số lựa chọn.

Không đưa mật khẩu rõ vào `values.yaml` commit Git. Helm release metadata có thể lưu rendered manifest và values theo backend/cơ chế phiên bản, nên quyền đọc release cũng cần xét. Dùng secret manager/External Secrets hoặc tham chiếu Secret được cấp theo quy trình; nếu chart có khả năng tạo Secret, hiểu rõ dữ liệu đi qua CI/log/history. `helm template` output có thể chứa secret, vì vậy không đính kèm nguyên bản vào PR/log public.

## Upgrade, rollback và quan hệ với Argo CD

Helm upgrade thay resource theo manifest mới; Kubernetes tiếp tục rollout. `helm upgrade` thành công ở cấp API không chứng minh readiness hoặc chức năng. `helm rollback` khôi phục release revision Helm theo khả năng công cụ nhưng không rollback DB migration, dữ liệu hay hệ thống ngoài chart. Nếu Argo CD quản lý một Application từ Helm chart, Argo render chart rồi áp manifest; không nên tự chạy `helm upgrade` vào cùng resource và kỳ vọng Argo giữ sửa tay. Quy định rõ ai là owner của release: CLI Helm hay GitOps controller.

**Ca lỗi có lời giải:** sau upgrade, Service vẫn tồn tại nhưng không có backend. Đọc rendered Deployment/Service: selector có còn khớp Pod labels không? Pod có Ready không? Probe path/port từ values có đúng không? Nếu chart template đổi label nhưng Service selector dùng helper cũ, Kubernetes chấp nhận hai resource mà traffic vẫn lỗi. Sửa chart, render, so diff, deploy staging rồi smoke test; tăng replica không sửa selector.

**Câu hỏi:** vì sao chart version 2.0 không chắc app image là 2.0? Vì version gói và image reference là trường khác. **Câu hỏi:** vì sao `helm lint` xanh chưa đủ? Nó kiểm tra phần cấu trúc/template nhất định, không chứng minh image pull, RBAC, storage hay nghiệp vụ. **Câu hỏi:** rollback release có xóa bảng DB mới? Không; DB nằm ngoài phạm vi bản manifest của chart và cần migration/restore plan riêng.

Bạn đạt bài khi có thể đọc chart từ values tới manifest, giải thích một diff upgrade, làm lỗi key/selector trong lab và khôi phục. Đối chiếu [Helm chart guide](https://docs.helm.sh/docs/topics/charts/) và [Helm chart best practices](https://docs.helm.sh/docs/chart_best_practices/) theo phiên bản CLI đang dùng.
