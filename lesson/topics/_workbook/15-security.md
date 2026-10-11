## Bảo vệ đường build và artifact

Giả sử developer merge code an toàn nhưng pipeline tải một package từ registry public bằng version range rộng. Một bản package mới độc hại có thể vào image mà source repo không đổi. Khóa dependency, dùng registry/allowlist phù hợp, tạo SBOM, scan và lưu provenance/digest giúp phát hiện và tái hiện. Nhưng lockfile không tự bảo vệ nếu attacker sửa lockfile qua PR được duyệt kém; reviewer phải hiểu thay đổi dependency và pipeline. Promotion nên dùng cùng artifact bất biến từ staging đến production, không rebuild với dependency khác.

Một image digest được ký hoặc có attestation tăng niềm tin về nguồn/build theo policy, nhưng phải kiểm tra ai giữ key/identity ký, build runner có đáng tin không và admission có thực thi policy không. “Có chữ ký” từ một pipeline đã bị chiếm không chứng minh code lành. Bảo mật supply chain là nhiều lớp: quyền source, runner, dependency, registry, deployment và runtime.

## CVE triage bằng hai ví dụ

Scanner báo CVE critical ở thư viện A trong image, nhưng thư viện chỉ dùng bởi công cụ build và không có trong runtime image. Xác minh SBOM/runtime contents trước khi quyết định; có thể không phơi lộ production nhưng vẫn cần vá pipeline/build. Scanner báo CVE medium ở endpoint public có exploit hoạt động; ưu tiên có thể cao hơn. Ma trận triage nên ghi severity, exploitability, exposure, asset impact, compensating control, owner và deadline. Không “ignore forever” bằng một comment thiếu bằng chứng.

## Phân quyền Kubernetes theo hành động

App Notes API cần đọc ConfigMap/Secret của chính nó khi start? Nhiều app nhận env/mount do kubelet cấp, không cần token gọi Kubernetes API trực tiếp. Nếu không dùng API, tắt automount ServiceAccount token theo chính sách để giảm bề mặt. Argo CD controller cần tạo Deployment/Service ở namespace được cấp, nhưng không nhất thiết được sửa mọi cluster-scoped resource. `kubectl auth can-i` và review RoleBinding/ClusterRoleBinding giúp kiểm tra quyền cụ thể; một quyền wildcard `*` trên `*` là tín hiệu phải giải thích. NetworkPolicy default-deny cần rule DNS/DB/telemetry thật, test từ Pod và theo dõi lỗi.

### Ca lộ secret trong Git

Thứ tự: thu hồi/rotate secret thật, kiểm tra audit và tác động, chặn pipeline/deploy phụ thuộc secret cũ theo kế hoạch, rồi làm sạch lịch sử theo quy trình nếu cần. Không chỉ xóa dòng ở commit mới. Sau đó thêm secret scanning/gate, hướng dẫn dev dùng secret manager/local env an toàn, và kiểm tra backup/fork/cache chứa bản cũ. Trong incident report ghi thời gian phơi lộ và quyền của credential, không sao chép giá trị secret.

Bạn đạt bài khi viết được threat model có ba attack path thực, chọn controls ở đúng lớp và giải thích vì sao scan/secret manager không phải “nút an toàn”. Nguồn: [OWASP Top 10:2025](https://top10.owasp.org/2025/0x00_2025-Introduction/), [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final).
