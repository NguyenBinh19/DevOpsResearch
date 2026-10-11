## Mô hình điều khiển và inventory

Ansible chạy từ control node tới managed node thường qua SSH/WinRM, dùng inventory xác định host/group và playbook mô tả task. Bạn không cần agent chạy nền trên từng Linux host trong mô hình phổ biến. Một playbook đúng cần xác định host nào, user/quyền nào, biến nào, và task nào được phép thay đổi. `hosts: all` với inventory production rộng là rủi ro nếu chưa xem phạm vi; dùng group riêng và `--limit` cho lab. Ansible Vault mã hóa dữ liệu nhạy cảm trong file nhưng không tự giải quyết mọi vấn đề về phân quyền, rotation hay secret trong log.

Idempotent là chạy lại với cùng desired state mà không tạo thay đổi ngoài ý muốn. Dùng module như `file`, `template`, `package`, `service` thay vì shell command không có điều kiện nếu có thể. Handler chỉ chạy khi task notify có thay đổi, ví dụ template Nginx thay thì reload service. Cần kiểm tra template trước reload để tránh đưa config lỗi vào production. `check mode`/`diff` giúp preview nhưng không bảo đảm mọi module mô phỏng chính xác; review và lab vẫn cần thiết.

## Lab an toàn trên một VM

Tạo inventory chỉ có VM lab và xác nhận IP/SSH user. Viết playbook tạo `/tmp/devops-mentor-lab` và một file text với nội dung do biến `lesson_version` điều khiển. Chạy `ansible-playbook -i inventory.ini playbook.yml --limit lab`; ghi số task `ok`/`changed`. Chạy lần hai, kỳ vọng `changed=0`. Đổi `lesson_version`, dùng `--check --diff` để xem dự đoán rồi chạy thật. Kiểm tra nội dung file trên VM. Cuối lab, dùng playbook riêng xóa đúng file lab; không chạy task xóa cả thư mục nếu chưa xác nhận đường dẫn.

```yaml
- hosts: lab
  become: false
  vars:
    lesson_version: "v1"
  tasks:
    - name: Create lab directory
      ansible.builtin.file:
        path: /tmp/devops-mentor-lab
        state: directory
        mode: '0755'
    - name: Write version marker
      ansible.builtin.copy:
        dest: /tmp/devops-mentor-lab/version.txt
        content: "{{ lesson_version }}\n"
        mode: '0644'
```

Nếu task thứ hai luôn báo changed, đọc module/biến và nội dung file trước khi chấp nhận. Một playbook `changed=0` chưa chứng minh service khỏe; chạy health check ngoài playbook hoặc module kiểm tra phù hợp. Với nhiều host, dùng rolling batches/serial và health check giữa các nhóm để tránh restart toàn bộ fleet cùng lúc.

## Ansible trong hạ tầng hybrid

Trên VMware/cloud, VM được tạo bằng một công cụ IaC, sau đó Ansible cấu hình OS, user, Nginx/HAProxy hoặc agent monitoring. Inventory có thể tĩnh cho lab, động cho fleet thay đổi; cần tránh host cũ/IP tái sử dụng dẫn tới chạy sai máy. Với kubespray, các playbook cài Kubernetes trên nhiều node, nhưng bạn vẫn phải quản lý phiên bản OS/runtime, backup control plane, etcd, storage/network plugin và upgrade. Không coi "playbook xanh" là bằng chứng cluster production HA.

**Case:** playbook update Nginx template trên 20 host, reload đồng thời, 30% request lỗi. Phân tích vì sao cần validate config trước reload, chạy từng batch, tách LB backend đang drain, kiểm tra health sau mỗi batch và có bản config trước để rollback. Ranh giới kiểm soát: Ansible thay file/service; LB và ứng dụng vẫn cần telemetry để xác nhận người dùng không bị ảnh hưởng.
