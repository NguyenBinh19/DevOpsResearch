# Chuyên đề 9 - Azure DevOps trong môi trường doanh nghiệp

JD 2 yêu cầu Azure thực hành, bảo mật ứng dụng và khả năng tự động hóa. Chuyên đề này nối các dịch vụ thành một kiến trúc thay vì học tên từng nút trong portal. Dịch vụ, giá và giới hạn thay đổi; trước lab có tính phí phải đọc trang Microsoft Learn và pricing hiện hành, đặt ngân sách và ghi cách xóa.

```text
User --HTTPS--> App Service --private DNS/endpoint--> Azure SQL
                    |                
                 Key Vault (managed identity)
                    |
               Blob Storage -> Service Bus -> Function worker
                    |
          App Insights / Log Analytics / alerts
```

Ở mỗi mũi tên, tách bốn câu hỏi: network có tới được không, TLS có đúng không, identity là ai và quyền dữ liệu có đủ không. Một lỗi 403 khác một lỗi DNS dù người dùng đều thấy chức năng thất bại.

## Bài 1. Resource group, identity và mạng

Azure tổ chức tài nguyên theo tenant, subscription, resource group và resource. Tenant liên quan identity; subscription là phạm vi billing/quản trị; resource group nhóm tài nguyên có vòng đời phù hợp. Đặt một ứng dụng trong resource group không tự khiến các tài nguyên có cùng quyền hoặc cùng network. Cần xem RBAC, VNet, route và NSG riêng.

Microsoft Entra ID xác thực identity; Azure RBAC quyết định identity có thể thực hiện hành động nào trên scope nào. Managed identity là identity gắn với tài nguyên Azure, giúp ứng dụng lấy token mà không lưu password client trong cấu hình. Ví dụ App Service cần đọc secret ở Key Vault: cấp managed identity cho App Service và quyền đọc đúng secret. Nếu lỗi 403, kiểm tra identity thực tế, scope/role hoặc access policy, network restriction và log; đừng gắn quyền Owner toàn subscription để thử.

VNet là mạng riêng logic; subnet chia địa chỉ; NSG lọc traffic theo rule. Private Endpoint đưa một dịch vụ Azure vào VNet qua IP private. Tuy nhiên, private endpoint cần DNS trỏ đúng private IP; tạo endpoint mà client vẫn phân giải tên public thì đường đi có thể không như mong muốn. Private endpoint cũng không tự bảo đảm đường public đã bị tắt; cần xem cấu hình dịch vụ đích. Đây là lỗi phỏng vấn và vận hành phổ biến vì có nhiều lớp cùng tham gia.

### Bài tập luồng truy cập

Vẽ browser -> App Service -> Azure SQL. Cho người dùng truy cập App Service qua HTTPS; App Service vào SQL qua private endpoint và managed identity. Ghi ở mỗi mũi tên: DNS, IP public/private, TLS, identity và quyền. Giả sử SQL trả lỗi truy cập: phân biệt lỗi DNS/route/NSG với lỗi RBAC/database authorization bằng tín hiệu nào? Một kết nối TCP thành công không chứng minh truy vấn được phép.

## Bài 2. Dịch vụ ứng dụng và dữ liệu

App Service chạy ứng dụng web/API theo mô hình managed; bạn vẫn quản lý mã, cấu hình, identity và release. Azure Functions phù hợp các handler theo sự kiện hoặc yêu cầu, nhưng cần hiểu trigger, timeout, cold start và khả năng chạy lại. Storage có nhiều loại như blob/file/queue theo mục đích. Azure SQL là database quan hệ managed; Service Bus là broker cho message/queue/topic. Chọn dịch vụ bằng yêu cầu: request đồng bộ hay công việc nền, dữ liệu quan hệ hay object, độ trễ, durability và cách phục hồi.

Ví dụ ứng dụng nhận file: API ghi metadata vào Azure SQL, file vào Blob Storage, phát message sang Service Bus để xử lý nền. Worker Azure Function nhận message, tạo thumbnail và cập nhật trạng thái. Một message có thể được giao lại khi xử lý thất bại; handler cần tính đến idempotency để tránh tạo kết quả trùng. Nếu Storage không sẵn sàng, API cần trả lỗi có ý nghĩa và không ghi metadata giả rằng file đã được lưu.

Key Vault giữ secrets/keys/certificates; không phải nơi thay thế mọi file cấu hình. Cấu hình không nhạy cảm có thể ở app settings hoặc hệ quản lý cấu hình phù hợp; secret cần quyền hẹp, rotation và audit. Khi app lỗi sau rotation, hỏi token/secret nào, phiên bản nào, cache khi nào hết hạn và app đã reload chưa.

### Lab chi phí thấp theo từng bước

Trước tiên chỉ dùng Microsoft Learn sandbox hoặc sơ đồ nếu bạn chưa có Azure subscription/budget. Nếu có tài khoản thử, đặt budget/cảnh báo, xác nhận subscription và region, tạo resource group lab có tên riêng. Tạo **một** dịch vụ đơn giản theo tutorial chính thức, ghi ID, SKU, giá dự kiến và cách truy cập; kiểm tra rồi xóa resource group lab sau khi đã chắc chắn nó không chứa dữ liệu khác. Sau đó mới mở rộng tới private endpoint/SQL, vì nhiều dịch vụ kết hợp có thể tạo phí đáng kể. Ghi hóa đơn thực tế sau lab để hiệu chỉnh ước tính.

## Bài 3. Azure DevOps Pipelines và release governance

Azure Pipelines định nghĩa stages, jobs và steps trong YAML. Stage có thể là build, test, deploy staging, deploy production. Mỗi stage cần đầu vào/đầu ra và điều kiện rõ. Pipeline nên build artifact một lần từ commit cụ thể, kiểm tra, rồi promotion cùng artifact qua môi trường. Service connection cấp quyền để pipeline nói chuyện với Azure; bảo vệ quyền này, tách môi trường và không để pull request chưa tin cậy dùng credential production.

Branch policy và pull request review giúp kiểm soát thay đổi vào nhánh phát hành. Environment approvals cho phép người có trách nhiệm xem bằng chứng trước thay đổi rủi ro. Approval không thay test: người duyệt cần biết commit, artifact, kết quả test, scan, plan IaC, tác động và rollback. Release notes nên mô tả thay đổi người dùng/hạ tầng/dữ liệu, không chỉ liệt kê commit message.

### Bài tập thiết kế pipeline

Viết YAML giả lập theo bốn stage: validate (lint/unit test), build (image/artifact), deploy-test (smoke/integration), deploy-prod (approval, rollout, kiểm tra sau triển khai). Vẽ đường đi của secret và service connection. Nếu integration test ở test fail, production stage phải làm gì? Nếu deployment production thành công nhưng smoke fail, ai nhận alert và cách rollback? Đừng tạo connection cloud thật chỉ để hoàn thành bài tập giấy.

## Bài 4. Bicep, ARM và Terraform trong Azure

ARM là nền tảng quản lý/deploy tài nguyên Azure; ARM template dùng JSON. Bicep là ngôn ngữ khai báo gọn hơn cho Azure, biên dịch thành ARM template. Terraform dùng state riêng và provider để quản lý Azure cùng các nền tảng khác. Không nên gọi Bicep là "Terraform của Microsoft" rồi bỏ qua khác biệt state, lifecycle và cách preview. Khi làm việc trong tổ chức, lựa chọn còn chịu ảnh hưởng governance, kỹ năng đội ngũ và hệ thống hiện có.

Bicep có what-if để xem thay đổi dự kiến; Terraform có plan. Cả hai cần review và phân quyền. Không đặt bí mật trong file tham số được commit. Nếu một tài nguyên được quản lý bởi cả hai công cụ hoặc sửa tay thường xuyên, drift và quyền sở hữu trở nên mơ hồ. Quy định rõ tài nguyên nào do pipeline nào quản lý.

### Bài tập so sánh

Lấy một resource group và một storage account làm ví dụ. Viết bảng: nơi khai báo, cách preview, trạng thái lưu ở đâu, ai apply, cách xử lý rollback và drift. Không cần thuộc cú pháp hết; mục tiêu là hiểu quy trình thay đổi. Sau đó đọc một mẫu Bicep chính thức và một mẫu Terraform Azure, chỉ ra resource, parameter/variable và output.

## Bài 5. Application Insights, Log Analytics và KQL

Application Insights theo dõi ứng dụng: request, dependency, exception và trace tùy cấu hình instrumentation. Log Analytics Workspace lưu/truy vấn log Azure Monitor; KQL là ngôn ngữ truy vấn để lọc, nhóm và tính số liệu. Metrics giúp thấy xu hướng nhanh; log và trace giúp điều tra chi tiết. Luôn biết nguồn dữ liệu, sampling/retention và chi phí ingest. Nếu không có telemetry từ app, dashboard chỉ nhìn hạ tầng sẽ bỏ sót lỗi business.

Ví dụ sau release, 5xx tăng ở endpoint POST /notes. Truy vấn cần lọc đúng ứng dụng, thời gian và operation; nhóm theo version hoặc dependency để xem lỗi mới có gắn với release không. KQL có toán tử lọc, project và summarize; khi học, viết câu hỏi bằng tiếng Việt trước, rồi mới chuyển thành truy vấn. Một truy vấn trả 0 dòng có thể do không có lỗi, cũng có thể do sai bảng/time range hoặc telemetry chưa được gửi.

## Bài 6. Bảo mật ứng dụng và tự động hóa có kiểm soát

JD 2 còn yêu cầu OWASP Top 10, threat modeling, SAST/DAST/SCA, CVE và least privilege. Với ví dụ ứng dụng tải file vào Blob Storage rồi phát message xử lý nền, tài sản gồm file người dùng, metadata, credential và token; điểm vào gồm API, Service Bus message, storage event và pipeline. Hỏi theo STRIDE: ai có thể giả mạo người dùng/message; dữ liệu có thể bị sửa; hành động có audit; file có bị lộ; hệ thống có thể bị nghẽn; quyền có bị leo thang. Với mỗi rủi ro, ghi một biện pháp và phép kiểm tra: giới hạn loại/kích thước file, token đúng audience, quét dependency, quyền Storage tối thiểu và log không chứa secret.

SAST tìm vấn đề trong source; SCA tìm dependency có lỗ hổng đã biết; DAST thử ứng dụng đang chạy. CVE cần triage theo phiên bản thực dùng, đường code, cấu hình, độ phơi bày và bản vá. Quy trình ghi mức ảnh hưởng, owner, deadline, mitigation và bằng chứng khi đóng. Pipeline phải quét lại sau khi nâng dependency/image.

### Bài tập quyền tối thiểu

Liệt kê ba identity: developer đọc log, App Service đọc đúng secret Key Vault và ghi Blob, pipeline triển khai vào một resource group. Với từng identity, ghi scope nhỏ nhất, hành động cần, cách cấp token và cách thu hồi. Kiểm tra riêng quyền control plane Azure RBAC và quyền data plane của dịch vụ đích; thấy resource trên portal không luôn đồng nghĩa đọc được dữ liệu bên trong.

## Bài 7. AI hỗ trợ remediation: nhánh tùy chọn

Sau khi làm chủ pipeline, identity, logging và rollback, có thể thiết kế agent đọc ticket bảo mật, phân loại, thu bằng chứng, đề xuất thay đổi và tạo PR. Agent không nên tự đóng ticket hoặc sửa production chỉ vì mô hình trả lời tự tin. Ticket/tài liệu bên ngoài có thể chứa hướng dẫn độc hại; chỉ cấp quyền cần thiết, ghi audit, yêu cầu approval cho thay đổi rủi ro và dùng kiểm tra xác định để quyết định pass/fail.

Diễn tập trên giấy: ticket yêu cầu xoay secret. Viết luồng xác minh scope -> tìm nơi dùng -> lập kế hoạch -> PR -> test môi trường thấp -> approval -> rotation/rollout -> xác nhận request -> thu bằng chứng -> đóng ticket. Chỉ ra bước máy có thể làm, bước người duyệt, và phương án phục hồi nếu secret mới làm app lỗi. Đây là bài thiết kế, không cấp token cloud thật cho agent lab.

## Case study có lời giải: Private Endpoint đã tạo nhưng SQL vẫn lỗi

**Bối cảnh:** nhóm vừa bật Private Endpoint cho Azure SQL; App Service báo kết nối timeout, portal vẫn cho thấy cả hai resource Running. Đi theo bốn lớp: (1) DNS từ môi trường chạy App Service đang phân giải FQDN SQL thành IP nào; (2) App Service có VNet integration/route tới private IP không; (3) NSG/firewall và dịch vụ đích có chấp nhận kết nối không; (4) token/DB user có quyền không. Nếu timeout trước TLS, sửa RBAC trước là sai hướng. Nếu TCP/TLS thành công nhưng SQL trả lỗi login, network có thể đã đúng; kiểm tra identity và quyền trong DB.

**Bằng chứng kết thúc:** truy vấn thử từ đúng runtime identity thành công, public path được cấu hình theo chính sách, telemetry ghi độ trễ và lỗi trở về baseline. Chỉ kiểm tra từ laptop kỹ sư không chứng minh App Service có cùng đường mạng. Ghi diagram DNS/route cuối cùng để người sau không tạo endpoint trùng hoặc mở lại public access khi gặp lỗi.

### Cổng năng lực

Bạn vẽ được App Service/Function/Storage/SQL/Service Bus cùng identity/network; giải thích private endpoint + DNS; thiết kế pipeline có môi trường và quyền; so sánh Bicep/ARM/Terraform; đề xuất truy vấn và cảnh báo từ App Insights/KQL. Nếu chưa có Azure lab trả phí, ghi rõ phần nào mới học qua tài liệu và thiết kế.

## Nguồn chính thức

- Azure Well-Architected Framework: https://learn.microsoft.com/azure/well-architected/
- Private Endpoint: https://learn.microsoft.com/azure/private-link/private-endpoint-overview
- Managed identity: https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview-for-developers
- Azure Pipelines YAML: https://learn.microsoft.com/azure/devops/pipelines/yaml-schema/?view=azure-pipelines
- Bicep overview: https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview
- Azure Monitor logs/KQL: https://learn.microsoft.com/azure/azure-monitor/logs/log-query-overview
