# Classification_Emails

## Mục đích dự án
Classification_Emails là một dự án ứng dụng AI sử dụng mô hình BERT để phân loại nội dung email vào các nhóm chủ đề như quảng cáo, giải trí, bạn bè, spam, học tập, công việc. Dự án giúp tự động nhận diện và phân loại email, hỗ trợ quản lý hộp thư hiệu quả hơn.

## Tính năng chính
- **Phân loại email với BERT**: Sử dụng mô hình BERT để xác định chủ đề của email.
- **Ứng dụng giao diện PyQt6**: Cho phép người dùng nhập nội dung email, chọn ví dụ mẫu, và nhận kết quả phân loại trực quan.
- **Thu thập dữ liệu email từ Gmail**: Cung cấp notebook để crawl và xử lý dữ liệu email từ tài khoản Gmail cá nhân.
- **Huấn luyện mô hình phân loại**: Notebook đào tạo mô hình phân loại email với các nhãn chủ đề cụ thể.

## Nhóm phân loại
Các email được phân loại vào một trong các nhóm sau:
- advertising (quảng cáo)
- entertainment (giải trí)
- friends (bạn bè)
- spam
- study (học tập)
- work (công việc)

## Cấu trúc dự án
- `Emails_Classification_App.py`: Ứng dụng giao diện người dùng dựa trên PyQt6, tích hợp mô hình BERT để phân loại email.
- `crawl_data.ipynb`: Notebook dùng để lấy và xử lý dữ liệu email từ Gmail.
- `Train_detec_model.ipynb`: Notebook huấn luyện mô hình BERT cho bài toán phân loại email.

## Hướng dẫn cài đặt

### 1. Clone repository
```bash
git clone https://github.com/HMinhAi/Classification_Emails.git
cd Classification_Emails
```

### 2. Cài đặt môi trường Python
Nên sử dụng Python >= 3.9 và pip.
```bash
pip install -r requirements.txt
```

Các thư viện chính:
- PyQt6
- torch
- transformers
- pandas
- google-auth, google-auth-oauthlib, google-api-python-client (dùng cho crawl_data.ipynb)

### 3. Cài đặt mô hình BERT
- Mô hình và tokenizer được tải từ `bert-base-uncased` thông qua thư viện transformers.
- Trained checkpoint đặt tại `./results/checkpoint-380` (có thể cần huấn luyện lại nếu chưa có file checkpoint).

### 4. Chạy ứng dụng phân loại email
```bash
python Emails_Classification_App.py
```
Ứng dụng sẽ hiển thị cửa sổ cho phép nhập nội dung email, chọn ví dụ mẫu và nhận kết quả phân loại.

## Hướng dẫn crawl dữ liệu email từ Gmail
- Chạy notebook `crawl_data.ipynb`.
- Làm theo hướng dẫn xác thực OAuth và lấy email từ Gmail về dưới dạng pandas dataframe gồm các trường: index, email_from, data, label.

## Hướng dẫn huấn luyện mô hình
- Chạy notebook `Train_detec_model.ipynb` để huấn luyện mô hình mới trên dữ liệu đã crawl.
- Điều chỉnh các tham số huấn luyện (epochs, batch_size, learning_rate) phù hợp với tài nguyên máy.

## Ví dụ phân loại
Một số ví dụ email mẫu trong ứng dụng:
- "Bạn đã trúng thưởng 1000$!" → spam
- "Khuyến mãi cuối tuần giảm giá 50%" → advertising
- "Hẹn gặp bạn cuối tuần để uống cafe" → friends
- "Lịch họp dự án diễn ra vào chiều thứ Tư" → work
- "Sự kiện giải trí lớn diễn ra vào tối nay" → entertainment
- "Đừng quên làm bài tập về nhà" → study

## Tác giả
- [HMinhAi](https://github.com/HMinhAi)

## License
Chưa cung cấp (vui lòng bổ sung thông tin giấy phép nếu cần).

---
Tham khảo repo: [https://github.com/HMinhAi/Classification_Emails](https://github.com/HMinhAi/Classification_Emails)
