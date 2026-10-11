## Từ playbook đến trạng thái: một ví dụ đầy đủ

Giả sử cần cấu hình Nginx trên 20 VM. Inventory chia `web_staging` và `web_production`; role cài package phiên bản được phê duyệt, render upstream config, validate bằng `nginx -t`, notify handler reload và gọi smoke test qua LB. Mỗi bước có owner và điều kiện. Nếu cài package “latest” mỗi lần run, bạn có thể thay version ngoài kế hoạch. Nếu handler reload trước khi validate, lỗi syntax gây outage. Nếu smoke test chỉ gọi localhost của một VM, LB tới host khác vẫn có thể lỗi. Playbook cần làm **đúng mục tiêu vận hành**, không chỉ chạy thành công.

Ví dụ pseudocode YAML cho một task an toàn:

```yaml
- name: Render Nginx upstream config
  ansible.builtin.template:
    src: notes.conf.j2
    dest: /etc/nginx/conf.d/notes.conf
    owner: root
    group: root
    mode: '0644'
  notify: Reload Nginx
```

Đây là **mẫu để đọc**, không phải playbook hoàn chỉnh: nó chưa kiểm tra toàn cấu hình trước khi thay file. Với Nginx, một fragment trong `conf.d` thường phải được kiểm tra trong ngữ cảnh main config, nên không thể tùy tiện dùng `nginx -t -c %s` như thể `%s` là main config. Trong thực tế hãy dùng một bước validation phù hợp với layout config của bạn trên VM lab/staging, rồi chỉ reload khi cấu hình hợp lệ; đọc module docs về `validate` và thử đường rollback. Không copy nguyên đoạn vào production.

## Biến, vault và quyền

Một role dùng `db_password` từ vault/secret manager; `debug: var=db_password` hoặc diff mode có thể lộ giá trị. `no_log: true` giảm hiện trong output cho task phù hợp, nhưng không thay quyền truy cập vault và log của ứng dụng. Inventory chứa SSH user/host, có thể nhạy cảm; repo public không nên chứa private key. Dùng `become` chỉ cho task cần root, không chạy toàn bộ playbook đặc quyền nếu không cần. Nếu một playbook trỏ `hosts: all` và inventory production có 500 host, rủi ro blast radius lớn; `--list-hosts`, `--limit`, `serial` và approval là guardrail.

## Idempotency và handler qua lỗi có lời giải

Task `shell: date > /etc/notes/reload-marker` luôn đổi file mỗi lần chạy. Nó báo changed mỗi lần; handler restart app mỗi lần, gây gián đoạn. Thay bằng module phù hợp nếu có, hoặc dùng điều kiện `creates`/`changed_when` dựa trên trạng thái thật, nhưng đừng làm `changed_when: false` để che thay đổi thực. Chạy playbook hai lần trong lab, so recap và trạng thái service; lần hai `changed=0` là bằng chứng mong đợi cho cấu hình ổn định. Nếu template chứa timestamp render mỗi lần, file luôn đổi dù cấu hình chức năng không đổi; bỏ timestamp khỏi config hoặc quản lý riêng.

### Lỗi network khác lỗi module

`UNREACHABLE` thường là SSH/DNS/port/auth/host key, chưa tới task cấu hình. `FAILED` ở package có thể là repo/permission/version; `FAILED` ở template có thể biến thiếu; `FAILED` ở handler reload có thể config không hợp lệ. Đọc recap theo host và task đầu tiên fail, không chỉ dòng lỗi cuối. Nếu 2/20 host fail sau batch đầu, dừng rollout, so điểm khác giữa hai host với 18 host khỏe: distro, network, disk, biến inventory, package version. Không retry toàn bộ production mù quáng.

## Kế hoạch rollout từng batch

Với 20 web VM, chọn `serial: 2` để thay 2 host một lúc, kiểm tra health từ LB trước khi tiếp. Nhưng nếu LB có minimum healthy backends hoặc traffic không phân đều, 2 có thể vẫn quá nhiều; tính capacity N-1 và quan sát. Nếu host không healthy sau thay đổi, rollback config/package trên batch đó trước khi mở batch tiếp. Cần biết handler/reload timing, connection draining và session state. Ansible có thể phối hợp với LB API nhưng cần quyền/transaction plan. Chạy `--check` trên staging là bước tốt, không thay diễn tập với traffic.

## Bài phỏng vấn có đáp án

**Ansible khác Terraform ở đâu?** Ansible thường tập trung cấu hình host/task qua inventory/module; Terraform theo dõi resource hạ tầng qua state và plan. Có giao nhau; xác định owner để tránh drift. **Kubespray là gì trong ngữ cảnh này?** Bộ playbook/roles triển khai Kubernetes trên hạ tầng, nhưng vận hành cluster production vẫn cần etcd backup, upgrade, CNI/CSI và SLO. **Vì sao playbook `ok=20 failed=0` chưa đủ?** Nó chứng minh task thực thi theo module; app có thể trả 502 do cấu hình logic sai, nên smoke test/metrics sau thay đổi là bắt buộc. Nguồn: [Ansible desired state/idempotency](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html).

## Bài thiết kế role nhiều môi trường

Bạn có staging và production dùng cùng Nginx role. Role default đặt port 8000; group_vars staging đổi 8080, production 8000. Nếu production cũng nhận biến từ host_vars cũ là 9000, kết quả có thể không như bạn nghĩ. Trước run, in inventory/host variables đã resolve cho **một host lab** và render template; ghi nguồn của giá trị cuối. Sau đó thay biến ở đúng lớp owner, không thêm một extra var vào pipeline để che xung đột. Nếu 20 host có config khác nhau không chủ đích, việc quản lý biến đã trở thành vấn đề vận hành.

**Tình huống:** một host trả `UNREACHABLE`, 19 host chạy xong; nếu pipeline báo xanh vì `ignore_unreachable`, môi trường ở trạng thái nửa mới nửa cũ. Quyết định có chấp nhận degraded capacity không, có cần rollback 19 host hay sửa SSH cho host thứ 20, và alert nào theo dõi phiên bản từng host. Ghi rõ rollout policy trước khi chạy. Đây là lý do cần batch, health check và inventory ownership chứ không chỉ một playbook idempotent.

**Tự kiểm tra:** vẽ đường controller -> SSH -> module -> file config -> handler -> Nginx -> LB -> người dùng. Ở mỗi mũi tên ghi một lỗi và lệnh/bằng chứng read-only đầu tiên. Nếu chỉ kiểm tra recap Ansible mà không kiểm tra LB request, bạn mới chứng minh lớp cấu hình, chưa chứng minh dịch vụ.

## Ranh giới với Windows và PowerShell

Trong JD Azure/hybrid, Ansible có thể quản lý host Windows qua WinRM/PowerShell modules, nhưng cách xác thực, transport, privilege và module khác Linux SSH. Không lấy một playbook `apt`/`systemd` rồi chạy trên Windows. Khi học, tách **mô hình chung** (inventory, desired state, idempotency, batch, verify) khỏi **module theo OS**. Nếu một script PowerShell được Ansible gọi qua `win_shell`, bạn vẫn phải kiểm soát exit code, thay đổi thực, secret trong output và khả năng chạy lại. Với tác vụ phức tạp, ưu tiên module chuyên dụng có semantics trạng thái rõ thay vì shell script mơ hồ.

**Câu hỏi:** một playbook chạy trên 20 Linux VM và 5 Windows VM cần phân nhóm thế nào? Tách group/role/module theo OS, dùng biến kết nối đúng, test mỗi nhánh ở staging, giới hạn batch và kiểm tra dịch vụ sau thay đổi. “Ansible hỗ trợ cả hai” không có nghĩa cùng task chạy được cả hai.
