## Kiến trúc Argo CD theo một thay đổi cụ thể

Argo CD có Application mô tả nguồn desired state (Git path, Helm chart hoặc nguồn được hỗ trợ), revision và destination cluster/namespace. Repo server lấy và render nguồn; application controller so desired với live state và quyết định sync; API/UI cho người vận hành quan sát/điều khiển theo RBAC. Người làm CI thường chỉ cần tạo artifact và cập nhật Git cấu hình triển khai qua PR. Khi merge, Argo CD phát hiện desired state mới và đồng bộ. Cần bảo vệ repository này như một control plane: ai merge vào production có thể thay đổi cluster dù không cầm `kubectl` trực tiếp.

```text
source commit -> CI/test/build -> image digest -> deployment Git PR
                                             -> review/merge
                                             -> Argo compare -> sync -> cluster
                                             -> smoke test / alert / rollback
```

`Synced` nghĩa là live state phù hợp với desired state theo cách Argo theo dõi; `Healthy` phản ánh health assessment của resource. Chúng không chứng minh API nghiệp vụ, DB, quyền người dùng hay đường từ Internet hoạt động. Nếu UI báo `OutOfSync`, xem diff: ai sửa live state, image/replicas/annotation nào khác, có HPA/controller khác cùng sở hữu field không. Cần giải quyết ownership, không tắt drift detection chỉ để dashboard xanh.

## Manual sync, auto-sync, prune và self-heal

Manual sync để người vận hành chủ động áp thay đổi. Auto-sync áp khi desired state đổi theo chính sách. Self-heal có thể đưa resource bị sửa tay về Git; prune có thể xóa resource live không còn trong desired state. Đây là các cài đặt mạnh. Trước khi bật prune, xem resource nào do Application quản lý, thứ tự migration và data/PVC có thể bị ảnh hưởng. Một PR xóa nhầm manifest có thể dẫn tới xóa resource khi prune bật. Dùng review, branch protection và policy để giảm rủi ro.

Nếu có emergency edit trực tiếp vào cluster, ghi incident và sớm đưa thay đổi tương ứng về Git hoặc revert edit có chủ đích; nếu không, lần sync tới có thể ghi đè. Tài khoản Argo CD vào cluster nên chỉ có quyền cần cho namespace/resource tương ứng; `cluster-admin` mặc định cho mọi app làm rộng blast radius. Tách quyền xem, sync và thay nguồn/destination theo vai trò.

## Lab không cần cloud: đọc và dự đoán trạng thái

Tạo repository lab chứa manifest `Deployment` và `Service` của Notes API, một nhánh `staging` và một nhánh `production` hoặc thư mục môi trường rõ ràng. Viết Application trỏ vào đúng path/namespace lab. Trước khi bấm sync, ghi dự đoán: resource nào tạo, image digest nào, namespace nào, Service sẽ có endpoint không. Nếu chỉ học offline, dùng bản manifest render từ Helm để so với live-state giả lập; ghi rõ đó là mô phỏng. Nếu có cluster local, cài Argo CD theo tài liệu chính thức, dùng namespace riêng và quyền lab; đồng bộ rồi `kubectl get` xác nhận.

Tạo drift bằng đổi replicas trực tiếp trong cluster; xem Argo báo khác gì. Khi self-heal bật, quan sát nó khôi phục về Git. Tiếp theo đổi image trong Git bằng PR và so sự kiện sync. Không cố ý xóa PVC/dữ liệu. Cuối lab, xóa Application và namespace lab theo đúng context, rồi ghi lại diff, event và thời gian đồng bộ.

## ApplicationSet, nhiều môi trường và app-of-apps

Khi có nhiều cluster/namespace/microservice, copy hàng trăm Application YAML bằng tay gây lệch. ApplicationSet tạo Application từ generator/template, ví dụ danh sách cluster hoặc thư mục. Tính năng này khuếch đại cả thay đổi tốt lẫn lỗi: một template sai có thể tác động nhiều môi trường. Test output, review phạm vi generator và tách production theo quyền/approval. Mô hình app-of-apps cũng cần kiểm soát rõ parent Application có thể tạo/sửa child nào. Không chọn vì “trông giống enterprise”; chọn khi số lượng và ownership thực sự cần.

## Rollback và dữ liệu

Rollback GitOps là thay đổi desired state, thường revert commit hoặc PR trỏ lại digest cũ. Cần xác nhận chart/values và cấu hình runtime cũng quay về trạng thái tương thích. Database migration có thể không đảo ngược. Nếu release thêm cột mới và app cũ không đọc cột ấy, rollback tương đối dễ; nếu release xóa cột cũ, app cũ có thể hỏng. Hãy thiết kế expand/contract schema và test phiên bản cũ-mới trong giai đoạn chuyển tiếp.

**Case phỏng vấn:** Argo `Healthy`, error rate tăng. Đầu tiên gắn request lỗi với version/digest và thay đổi vừa sync, kiểm tra route/Service/pod logs/dependency. Nếu chỉ pod mới lỗi, dừng sync/promotion, revert Git theo quy trình và xác nhận metric trở lại. Nếu mọi pod lỗi, kiểm tra dependency chung và tránh rollback vô ích. Postmortem ghi vì sao health check không bắt được luồng lỗi, bổ sung smoke test hoặc alert tương ứng.

## Đọc Application manifest từng trường

Ví dụ học tập dưới đây dùng repository ví dụ của dự án Argo CD. Nó giả định Argo CD đã được cài trong namespace `argocd` và cluster có thể lấy repository public. Đọc YAML trước khi áp; đổi destination/namespace chỉ sau khi hiểu quyền và context cluster.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook-lab
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: guestbook-lab
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
```

`metadata.namespace` là nơi lưu object Application, không phải namespace app. `source` nói Argo lấy desired state ở đâu; `targetRevision: HEAD` tiện cho lab nhưng production nên chọn ref/commit và quản trị branch rõ ràng. `destination` là cluster/namespace đích. `CreateNamespace=true` cho phép tạo namespace đích khi sync, với điều kiện Argo có quyền. Chưa có `automated`, nên cần sync chủ động. Chưa có `prune`, nên không mặc định xóa live resource bị bỏ khỏi Git. Sau khi hiểu, thay đổi từng option một và ghi tác động quan sát được.

### Lab đọc trạng thái có bằng chứng

1. Kiểm tra `kubectl config current-context`, namespace `argocd` và quyền lab. Chỉ thực hiện trên cluster riêng.
2. Lưu YAML trên thành `guestbook-lab.yaml`, chạy `kubectl apply -f guestbook-lab.yaml`. Đọc Application bằng `kubectl get application guestbook-lab -n argocd -o yaml`.
3. Xem status conditions, sync status, health status và events. Nếu dùng Argo UI/CLI, xem diff trước sync; dự đoán resource nào sẽ được tạo.
4. Sync thủ công trong UI/CLI theo hướng dẫn phiên bản đang dùng. Kiểm tra namespace `guestbook-lab`, Deployment/Service/Pod và request thực tế. `Synced`/`Healthy` chỉ là hai bằng chứng trong chuỗi.
5. Sửa manifest trong một fork/repo lab của bạn hoặc dùng bản sao local đã kiểm soát để tạo drift; so diff. Không chỉnh repository public bạn không sở hữu.
6. Dọn Application và namespace lab sau khi xác nhận resource nào do Argo tạo và có dữ liệu cần giữ không. Lưu status/diff/event trước khi xóa.

Nếu không cài cluster/Argo local, làm bài đọc manifest và dự đoán status trên giấy. Điều này là bài thiết kế, không ghi thành kinh nghiệm deploy Argo CD thật.

## Troubleshooting theo triệu chứng

**Application Unknown/ComparisonError:** repo server không lấy được Git, đường dẫn sai, credentials hoặc render Helm/Kustomize lỗi. Kiểm tra điều kiện Application, repo URL/ref/path, network tới Git và log repo server. Đừng sửa Deployment live khi desired manifest còn chưa render được.

**OutOfSync liên tục:** so diff; một admission controller, HPA hoặc người sửa tay có thể thay field. Tìm owner field và chính sách ignore differences nếu đó là khác biệt hợp lệ, nhưng phải hiểu hệ quả. Bật self-heal khi hai controller tranh field có thể gây lặp reconcile và nhiễu sự cố.

**SyncFailed:** API/admission từ chối manifest vì schema, quota, RBAC hoặc thứ tự dependency. Xem operation result và Kubernetes events; sửa nguồn Git, không chỉ `kubectl apply` thủ công rồi chờ Argo ghi đè.

**Synced nhưng Degraded:** manifest đúng nguồn nhưng workload không đạt health, ví dụ Pod ImagePullBackOff hoặc Deployment thiếu Ready replicas. Đi từ Pod events/logs, registry credential, resource quota và readiness. Nếu Service không có endpoint, xem selector/labels và Pod Ready.

**Synced/Healthy nhưng người dùng lỗi:** health assessment chưa kiểm tra nghiệp vụ. Dùng smoke test từ đúng đường người dùng, metric/error log/trace theo version, rồi quyết định rollback hoặc sửa dependency.

## Bảo mật và mô hình nhiều nhóm

Repository chứa manifest, chart/values hoặc Kustomize overlay có thể gián tiếp tạo RBAC, NetworkPolicy, Secret reference và image. Bảo vệ branch, yêu cầu review, scan manifest/policy và ghi audit người merge. Argo project giới hạn source repo/destination/resource theo nhóm; cùng với quyền Argo RBAC và Kubernetes RBAC, nó giảm blast radius. Đừng để một Application của đội A có thể đổi namespace production của đội B chỉ vì dùng chung Argo instance.

Image updater tự động hoặc bot tạo PR đổi digest có thể giảm thao tác lặp, nhưng cần kiểm soát nguồn image, chữ ký/provenance và cổng test. Một bot commit thẳng vào production config có thể vượt review; hãy đưa bằng chứng build/test/scan vào PR và xác định ai phê duyệt. Với secret, GitOps thường lưu **tham chiếu** tới external secret system hoặc dữ liệu mã hóa theo quy trình, không commit password rõ chữ.

## Bài tập phỏng vấn cuối: rollback trong 10 phút

Giả sử release mới làm 20% POST thất bại, Argo báo Synced/Healthy. Bạn có mười phút giảm tác động. Câu trả lời cần có thứ tự: xác nhận metric và version; dừng thay đổi tiếp; kiểm tra app cũ có tương thích schema; revert PR image digest trong deployment Git; sync và theo dõi rollout; smoke POST thật; xác nhận error rate giảm; ghi timeline. Nếu schema đã đổi phá vỡ app cũ, chọn mitigation khác như forward fix hoặc restore theo runbook có đánh giá mất dữ liệu. Sau sự cố, thêm smoke test luồng POST và cảnh báo gắn SLO.
