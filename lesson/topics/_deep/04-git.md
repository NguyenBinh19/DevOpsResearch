## Git có ba vùng cần phân biệt

Working tree là file bạn đang sửa; staging index là snapshot dự kiến đưa vào commit; repository lưu commit. `git status` cho biết thay đổi ở đâu; `git diff` xem phần chưa stage; `git diff --staged` xem đúng nội dung sẽ commit. Một commit tốt mô tả một ý nghĩa thay đổi, đủ nhỏ để review/revert. Branch cho phép phát triển riêng, nhưng merge vẫn cần xem diff và test. Conflict là Git không thể tự quyết nội dung hợp nhất; chọn một phía toàn bộ không phải lúc nào đúng.

Git history còn liên quan vận hành: release phải biết commit nào tạo artifact, config hạ tầng nào áp dụng, và commit nào rollback. Một tag release là nhãn cho commit; image digest là định danh artifact. Chỉ biết branch `main` không đủ vì nhánh tiếp tục di chuyển. Với GitOps, repository cấu hình triển khai là nguồn mong muốn; quyền merge vào branch production là quyền thay đổi production.

## Lab conflict có chủ đích

Trong repository lab riêng, tạo branch `feature-a` và `feature-b` từ cùng base. Sửa **cùng một dòng** cấu hình theo hai cách khác nhau, commit trên mỗi branch. Merge một branch rồi merge branch kia. Đọc conflict marker, quyết định giá trị đúng dựa trên yêu cầu của ứng dụng, sửa file, chạy kiểm tra và commit merge. Ghi `git log --graph --oneline --all` để giải thích lịch sử. Sau đó tạo một thay đổi độc lập trên nhánh mới và mở PR giả lập: mô tả mục tiêu, test, ảnh hưởng hạ tầng/dữ liệu, rollback. Không đưa `.env`, token hoặc file DB vào commit.

## Revert khác reset

`git revert` tạo commit mới đảo tác động của commit cũ, giữ lịch sử chia sẻ; thường phù hợp nhánh đã push. `git reset` thay đổi vị trí branch/local history, dễ gây rối nếu đã chia sẻ. Nhưng revert mã nguồn chưa chắc rollback hạ tầng hay dữ liệu: Terraform plan cần review, migration DB có thể không đảo ngược. Trong phỏng vấn, khi được hỏi "rollback release", hãy chỉ rõ bạn đang rollback commit, image, manifest, config hay schema.

## Branch governance và bảo vệ pipeline

Protected branch, review, required checks và quyền merge giúp giảm thay đổi không kiểm soát. Nhưng rule chỉ hiệu quả khi job CI thực sự kiểm tra artifact sẽ deploy và runner/secret không lộ cho PR không tin cậy. Một PR thay workflow để bỏ test hoặc in secret là thay đổi có rủi ro cao, cần review kỹ. Dùng lịch sử Git để truy tìm ai thay đổi gì, nhưng postmortem tập trung vào hệ thống kiểm soát và điều kiện cho lỗi lọt qua, không đổ lỗi cá nhân.
