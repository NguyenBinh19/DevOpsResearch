## Chart gồm những gì và được render ra sao?

Một chart là thư mục có `Chart.yaml` (tên và version), `values.yaml` (giá trị mặc định), `templates/` (manifest có biểu thức) và có thể có `charts/` dependency. Helm kết hợp chart + values để render YAML rồi gửi tới Kubernetes API. Cần đọc **YAML sau render**, không chỉ đọc template: một dấu cách, `default` hoặc điều kiện `if` có thể tạo resource khác bạn nghĩ. `helm lint` phát hiện một số lỗi cấu trúc; `helm template` cho đầu ra; Kubernetes API và admission policy còn có thể từ chối, và ứng dụng vẫn có thể lỗi sau khi resource được chấp nhận.

Phân biệt ba version: chart `version`, `appVersion` mô tả ứng dụng, và image tag/digest thực triển khai. `appVersion` không tự khóa image. Với release có thể kiểm chứng, pipeline ghi commit + chart version + image digest + values/environment. Hạn chế dùng `latest`; một tag có thể bị ghi đè, làm rollback không tái tạo được.

## Lab thực hành cụ thể với Notes API

Tạo chart `lesson/labs/helm-notes/` gồm `Chart.yaml`, `values.yaml`, `templates/deployment.yaml`, `templates/service.yaml`. Đặt `replicaCount: 1`, image lab và port 8000. Chạy `helm lint lesson/labs/helm-notes`; tiếp theo `helm template notes lesson/labs/helm-notes`. Trong output, kiểm tra: selector Deployment khớp label Pod; selector Service cũng khớp; containerPort và targetPort cùng 8000; resource requests/limits có ý nghĩa; image pull policy phù hợp cluster local. Chart dùng `emptyDir` cho SQLite **chỉ để học**: xóa Pod sẽ mất dữ liệu; production cần thiết kế persistence khác. Nếu chưa có image notes-api trong cluster, chỉ render/lint; đó là bài kiểm tra template, không giả vờ đã triển khai ứng dụng.

Thay `replicaCount=2` bằng `--set replicaCount=2`, render lại và so output. Thay `image.tag` bằng một tag không tồn tại rồi triển khai trên cluster lab (nếu có), quan sát Pod event. `helm status` có thể báo release đã tạo trong khi Pod chưa Ready; `kubectl rollout status`, Service endpoints và smoke test trả lời lớp vận hành. Dọn dẹp bằng `helm uninstall notes -n <namespace>` sau khi xác nhận đúng context.

### Các file tối thiểu

```text
helm-notes/
  Chart.yaml
  values.yaml
  templates/deployment.yaml
  templates/service.yaml
```

Trong template, dùng một nhãn ổn định như `app.kubernetes.io/name: notes-api` cho cả Deployment và Service. Values môi trường chỉ ghi sự khác biệt: hostname, replica count, resource, image digest, endpoint. Không copy cả chart cho staging và production; bản sao sẽ lệch. Không commit secret vào values; `helm template` và `helm get values` có thể làm lộ dữ liệu tùy cách dùng.

## Upgrade, lịch sử và rollback

`helm upgrade --install` tạo hoặc cập nhật release. Helm có release revision/history và có thể `helm rollback` về revision trước; cần hiểu rollback này áp lại manifest/values, không tự rollback dữ liệu đã đổi. Nếu chart thay PVC hoặc thực hiện hook migration DB, phải có kế hoạch cụ thể. `--atomic` hỗ trợ rollback trong một số tình huống upgrade lỗi nhưng không thay smoke test nghiệp vụ hay xử lý schema. Đọc diff/manifest trước, nhất là thay đổi xóa resource, Service, PVC và quyền RBAC.

**Case:** phiên bản mới có readiness 200 nhưng POST ghi DB 500. Helm release thành công; rollback image có thể cứu nếu schema tương thích. Nếu migration đã xóa cột cũ, rollback app sẽ vẫn lỗi. Cần release schema theo expand/contract và backup/restore được diễn tập trước khi đổi dữ liệu rủi ro. Câu trả lời phỏng vấn nên tách Helm release state với trạng thái sức khỏe ứng dụng.

## Chart dependency và trách nhiệm vận hành

Chart dependency giúp cài kèm service, nhưng đừng mặc định gom database production vào chart của app. Vòng đời database, backup, upgrade và permission thường khác app. Trong microservices, chart chung có thể giảm lặp nhưng nếu template quá nhiều điều kiện, việc review trở nên khó. Dùng cấu trúc nhỏ, tên rõ, values có schema/kiểm tra, và test render cho mỗi môi trường. Nếu dùng Argo CD để deploy chart, xác định ai là owner đồng bộ; tránh vừa `helm upgrade` thủ công vừa để Argo tự kéo về khác.
