## Một lần deploy Azure theo bằng chứng

CI build image có digest và test; IaC plan/what-if mô tả thay đổi hạ tầng; reviewer duyệt identity/network/storage; pipeline deploy staging bằng service connection phạm vi staging; smoke test gọi API thật; production gate duyệt digest đã thử. Sau deploy, xem App Insights request failure/latency và dependency SQL/Service Bus, so operation ID với mốc release. Nếu rollback, xác định app image, config, schema DB và queue messages có còn tương thích không. Azure DevOps Pipelines YAML giúp mô tả luồng nhưng không tự thay quyết định rủi ro.

### Case App Service không đọc Key Vault

App trả 500 ngay sau start vì không lấy được secret. Kiểm tra managed identity của đúng App Service slot/runtime, role/access policy trên đúng vault/secret, network/private endpoint của vault, DNS từ app và thời gian propagation. Một “Key Vault reference” trong config không chứng minh được phân giải ở runtime. Nếu staging slot có identity khác production slot, swap có thể đổi behavior. Giảm tác động bằng rollback config/slot theo runbook nếu tương thích; không copy secret vào plain app settings để chữa cháy mà không có kiểm soát.

## Bài tập KQL trên giấy

Bạn có bảng request với timestamp, operation_Id, url, resultCode, duration và bảng dependency có operation_Id, target, duration, success. Hãy lọc 15 phút quanh release, nhóm 5xx theo route và ghép các operation lỗi với dependency SQL để xem correlation. Nếu app chưa truyền operation ID tới downstream, phải thêm instrumentation; KQL không thể tự tạo mối liên hệ không có trong telemetry. Không thu thập body/token nhạy cảm chỉ để debug tiện.

**Câu hỏi:** Functions trả 202 sau khi gửi Service Bus, đã hoàn tất nghiệp vụ chưa? Chưa; consumer có thể còn backlog hoặc dead-letter. Theo dõi end-to-end correlation và age. Nguồn: [Azure Monitor/Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview), [Azure DevOps Pipelines](https://learn.microsoft.com/en-us/azure/devops/pipelines/).
