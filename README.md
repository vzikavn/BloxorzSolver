# Bloxorz Solver
**Đồ án 1 — CSC14003: Cơ sở Trí tuệ Nhân tạo (HCMUS)**

## 1. Giới thiệu
**Bloxorz 2.5D** là trò chơi giải đố lăn khối chữ nhật `1x1x2` trên mặt sàn lưới 2.5D. Mục tiêu của trò chơi là di chuyển khối lọt xuống ô đích ở tư thế đứng thẳng (`STANDING`) mà không bị rơi khỏi bàn cờ hoặc làm vỡ các ô gạch mỏng (`Fragile`).

Bên cạnh chế độ người chơi tự điều khiển, chương trình tích hợp sẵn 4 thuật toán tìm kiếm AI (**BFS, DFS, UCS, A\***) để tự động tìm lời giải, thống kê hiệu năng (thời gian, bộ nhớ, số nút mở rộng, số bước đi) và phát lại (Replay) trực tiếp trên giao diện.

---

## 2. Cài đặt & Chạy trò chơi

### Yêu cầu hệ thống
* **Python 3.8** trở lên (đã tích hợp sẵn thư viện đồ họa `tkinter`).
* Cài đặt thư viện phụ trợ (dùng khi chạy script thống kê thực nghiệm):
  ```bash
  pip install -r requirements.txt
  ```

### Khởi chạy trò chơi
Mở Terminal / Command Prompt tại thư mục gốc của dự án và chạy lệnh:
```bash
python main.py
```

*(Tùy chọn)* Chạy script đo đạc thực nghiệm và xuất bảng số liệu/biểu đồ tự động vào thư mục `results/`:
```bash
python benchmark.py
```

---

## 3. Cách chơi & Điều khiển

### Các loại ô có trong trò chơi
* **Sàn thường (Đá xám)**: Chịu được khối ở mọi tư thế (đứng thẳng hoặc nằm ngang/dọc).
* **Gạch mỏng (Cam đất - Fragile)**: Chỉ chịu được khối khi nằm ngang/dọc hoặc khối đơn `1x1x1`; nếu khối đứng thẳng `1x1x2` đè lên, gạch sẽ vỡ và thua cuộc.
* **Công tắc & Cầu**:
  * **Soft Switch (Đĩa tròn)**: Kích hoạt đóng/mở cầu khi bất kỳ phần nào của khối chạm vào.
  * **Heavy Switch (Chữ X)**: Chỉ kích hoạt khi khối đứng thẳng đè lên.
  * **Split Switch (Vòng màu tím)**: Tách khối đứng thẳng thành 2 khối đơn `1x1x1`. Hai khối đơn sẽ tự động gộp lại khi di chuyển đến 2 ô liền kề nhau.
* **Ô Đích (Hố sâu)**: Màn chơi hoàn thành khi khối `1x1x2` đứng thẳng ngay trên ô đích.

### Phím điều khiển
| Phím bấm / Thao tác | Chức năng |
| :--- | :--- |
| `↑` `↓` `←` `→` hoặc `W` `A` `S` `D` | Lăn khối theo 4 hướng Lên, Xuống, Trái, Phải |
| `Space` (Phím cách) | Chuyển đổi qua lại giữa 2 khối đơn `1x1x1` (khi đang tách khối) |
| `Z` hoặc `Backspace` | **Undo**: Hoàn tác bước đi vừa thực hiện |
| `R` | **Restart**: Chơi lại màn hiện tại từ vị trí xuất phát |
| **Chuột trái (Bảng bên phải)** | Chọn màn chơi trong danh sách cuộn hoặc bấm `Solve BFS / DFS / UCS / A*` để sử dụng các thuật toán tự động giải |
