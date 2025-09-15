import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import webbrowser

# Danh sách nhãn
labels = ['advertising', 'work', 'friends', 'study', 'entertainment', 'spam']

emails = [
    # Advertising (5)
    {"subject": "Khuyến mãi lớn", 
     "body": "Mua ngay hôm nay để nhận ưu đãi cực lớn! Chương trình chỉ kéo dài đến hết tuần này nên đừng bỏ lỡ. Chúng tôi cam kết mang đến cho bạn sản phẩm chất lượng với mức giá tốt nhất. Đăng ký nhận bản tin để cập nhật thêm nhiều khuyến mãi hấp dẫn trong thời gian tới. Cảm ơn bạn đã luôn đồng hành cùng thương hiệu của chúng tôi.", 
     "label": "advertising"},

    {"subject": "Ưu đãi đặc biệt", 
     "body": "Đừng bỏ lỡ cơ hội sở hữu sản phẩm mới ra mắt với nhiều tính năng vượt trội. Khi đặt hàng ngay hôm nay, bạn sẽ nhận được quà tặng đi kèm vô cùng giá trị. Số lượng sản phẩm có hạn và ưu đãi chỉ dành cho những khách hàng nhanh tay nhất. Hãy liên hệ ngay để được tư vấn chi tiết và tận hưởng dịch vụ tốt nhất từ chúng tôi.", 
     "label": "advertising"},

    {"subject": "Mua 1 tặng 1", 
     "body": "Chúng tôi mang đến ưu đãi đặc biệt: mua 1 sản phẩm sẽ được tặng thêm 1 sản phẩm bất kỳ trong danh mục. Chương trình chỉ kéo dài trong 3 ngày nên bạn hãy nhanh tay đặt hàng ngay. Đây là cơ hội tuyệt vời để vừa tiết kiệm vừa có thêm nhiều sản phẩm chất lượng. Hãy chia sẻ thông tin này cho bạn bè để cùng nhận ưu đãi.", 
     "label": "advertising"},

    {"subject": "Khuyến mãi cuối tuần", 
     "body": "Khuyến mãi siêu hấp dẫn cuối tuần: giảm giá 50% cho toàn bộ các mặt hàng trong cửa hàng. Chúng tôi đảm bảo giao hàng nhanh chóng và miễn phí cho đơn hàng từ 500,000 đồng trở lên. Ngoài ra, khách hàng thân thiết sẽ được tích thêm điểm để đổi quà. Hãy nhanh tay đặt hàng để không bỏ lỡ cơ hội này.", 
     "label": "advertising"},

    {"subject": "Sale cuối năm", 
     "body": "Khuyến mãi cuối năm đã chính thức bắt đầu với mức giảm giá lên đến 70%. Hàng trăm sản phẩm từ nhiều thương hiệu nổi tiếng đang chờ bạn lựa chọn. Đội ngũ chăm sóc khách hàng của chúng tôi luôn sẵn sàng hỗ trợ 24/7. Đừng quên kiểm tra giỏ hàng của bạn để đảm bảo không bỏ lỡ bất kỳ ưu đãi nào.", 
     "label": "advertising"},

    # Work (5)
    {"subject": "Báo cáo công việc", 
     "body": "Vui lòng hoàn thành báo cáo trước deadline để đảm bảo tiến độ dự án. Nếu gặp khó khăn, hãy liên hệ với quản lý trực tiếp để được hỗ trợ kịp thời. Mọi báo cáo cần được cập nhật trên hệ thống trước khi gửi bản cứng. Chúng ta cần phối hợp chặt chẽ để đạt mục tiêu chung và mang lại kết quả tốt nhất.", 
     "label": "work"},

    {"subject": "Lịch họp tuần", 
     "body": "Đội nhóm sẽ họp vào lúc 9h sáng mai tại phòng họp tầng 3 để trao đổi về kế hoạch tuần tới. Vui lòng chuẩn bị báo cáo tiến độ cá nhân và những vấn đề còn tồn đọng. Hãy đảm bảo rằng các tài liệu liên quan đã được cập nhật đầy đủ. Cuộc họp sẽ giúp chúng ta điều chỉnh kế hoạch và phân bổ nhiệm vụ hợp lý hơn.", 
     "label": "work"},

    {"subject": "Nộp báo cáo", 
     "body": "Báo cáo công việc tuần này cần được nộp trước 17h thứ Sáu. Vui lòng kiểm tra kỹ số liệu để tránh sai sót trong quá trình tổng hợp. Nếu cần hỗ trợ, hãy liên hệ với bộ phận IT để được giải quyết sớm. Đừng quên bổ sung các đề xuất cải tiến để nâng cao hiệu quả dự án.", 
     "label": "work"},

    {"subject": "Thông báo họp dự án", 
     "body": "Lịch họp dự án sẽ diễn ra vào chiều thứ Tư tại phòng họp lớn. Nội dung họp bao gồm đánh giá tiến độ và phân chia nhiệm vụ mới cho tuần tới. Đề nghị mọi người chuẩn bị ý kiến đóng góp trước khi đến họp. Sự tham gia đầy đủ của các thành viên sẽ giúp dự án đạt được kết quả như mong muốn.", 
     "label": "work"},

    {"subject": "Đào tạo kỹ năng", 
     "body": "Công ty sẽ tổ chức buổi đào tạo kỹ năng mềm vào tuần tới dành cho toàn bộ nhân viên. Đây là cơ hội tốt để nâng cao khả năng giao tiếp và làm việc nhóm. Vui lòng đăng ký tham gia qua đường link đính kèm trong email này. Mọi chi tiết về chương trình đào tạo sẽ được gửi đến bạn sau khi hoàn tất đăng ký.", 
     "label": "work"},

    # Friends (5)
    {"subject": "Đi chơi cuối tuần", 
     "body": "Cuối tuần này nhóm mình dự định tổ chức một buổi dã ngoại nhỏ ở công viên. Mỗi người sẽ chuẩn bị một món ăn để cùng nhau chia sẻ. Hy vọng bạn sẽ tham gia để có thêm nhiều kỷ niệm vui vẻ. Nếu bạn đồng ý, hãy xác nhận sớm để mình lên danh sách đồ ăn và hoạt động.", 
     "label": "friends"},

    {"subject": "Hẹn gặp lại", 
     "body": "Hẹn gặp lại dịp tới, mình rất mong được gặp bạn và mọi người. Lần trước đi chơi thật sự rất vui và để lại nhiều kỷ niệm. Hy vọng lần này sẽ có thêm nhiều hoạt động thú vị hơn. Đừng quên mang theo máy ảnh để lưu lại những khoảnh khắc đáng nhớ nhé.", 
     "label": "friends"},

    {"subject": "Chia sẻ ảnh đẹp", 
     "body": "Mình vừa tải lên album ảnh chuyến đi vừa rồi cho mọi người cùng xem. Ai cũng khen bạn chụp ảnh rất tự nhiên và đẹp. Lần tới chúng ta có thể thử đi picnic ở ngoại ô để đổi gió. Nếu bạn biết địa điểm thú vị nào thì nhớ giới thiệu cho nhóm nhé.", 
     "label": "friends"},

    {"subject": "Dã ngoại công viên", 
     "body": "Nhóm dự định tổ chức một buổi picnic tại công viên trung tâm vào Chủ Nhật này. Sẽ có nhiều trò chơi tập thể để mọi người cùng tham gia. Hãy chuẩn bị thêm vài món ăn nhẹ để chúng ta cùng thưởng thức. Rất mong bạn sẽ tham gia để buổi dã ngoại thêm vui.", 
     "label": "friends"},

    {"subject": "Rủ đi cà phê", 
     "body": "Mình vừa tìm thấy một quán cà phê mới với không gian yên tĩnh và cực kỳ dễ thương. Đây là nơi lý tưởng để trò chuyện hoặc làm việc cuối tuần. Nếu bạn rảnh, chúng ta có thể ghé thử vào chiều thứ Bảy này. Đừng quên mang theo laptop nếu muốn làm việc cùng nhau nhé.", 
     "label": "friends"},

    # Study (5)
    {"subject": "Ôn tập thi", 
     "body": "Chúc bạn học tốt và đạt kết quả cao trong kỳ thi sắp tới. Đừng quên ôn lại các kiến thức trọng tâm và luyện đề thường xuyên. Hãy giữ gìn sức khỏe để có tinh thần thoải mái khi thi. Nếu gặp khó khăn, hãy nhờ thầy cô hoặc bạn bè hỗ trợ ngay.", 
     "label": "study"},

    {"subject": "Bài tập về nhà", 
     "body": "Đừng quên hoàn thành đầy đủ các bài tập về nhà đã được giao trong tuần này. Việc học đều đặn sẽ giúp bạn tiếp thu kiến thức hiệu quả hơn. Nếu có thắc mắc, hãy hỏi giáo viên để được giải đáp kịp thời. Ngoài ra, bạn cũng có thể học nhóm để trao đổi thêm kinh nghiệm.", 
     "label": "study"},

    {"subject": "Tài liệu học tập", 
     "body": "Tài liệu học tập mới đã được cập nhật trên hệ thống, bạn nhớ tải về nhé. Ngoài ra, hãy tham khảo thêm sách tham khảo để mở rộng kiến thức. Đừng quên luyện tập nhiều dạng bài tập khác nhau. Mình luôn sẵn sàng hỗ trợ nếu bạn cần thêm giải thích.", 
     "label": "study"},

    {"subject": "Lịch thi", 
     "body": "Lịch thi chính thức đã được công bố và bạn nên sắp xếp thời gian ôn tập hợp lý. Hãy chia nhỏ từng chủ đề để học từng phần một cách hiệu quả. Đừng để đến sát ngày thi mới bắt đầu ôn tập. Nếu thấy căng thẳng, hãy nghỉ ngơi một chút để giữ tinh thần thoải mái.", 
     "label": "study"},

    {"subject": "Bài tập tuần", 
     "body": "Bài tập về nhà tuần này khá nhiều và có một số dạng khó hơn bình thường. Bạn nên bắt đầu làm sớm để tránh bị áp lực vào cuối tuần. Nếu gặp bài khó, hãy thảo luận với bạn bè để tìm cách giải. Đừng quên kiểm tra kỹ bài làm trước khi nộp nhé.", 
     "label": "study"},

    # Entertainment (5)
    {"subject": "Sự kiện cuối tuần", 
     "body": "Tham gia sự kiện cuối tuần này để nhận nhiều phần quà hấp dẫn. Sẽ có nhiều hoạt động thú vị và các trò chơi tập thể. Ngoài ra còn có những tiết mục âm nhạc đặc sắc để bạn thưởng thức. Đừng quên rủ thêm bạn bè cùng tham gia cho thêm phần sôi động.", 
     "label": "entertainment"},

    {"subject": "Xem phim mới", 
     "body": "Tuần này có nhiều bộ phim mới ra mắt với nội dung hấp dẫn. Đây là dịp tuyệt vời để bạn và bạn bè cùng thư giãn sau những giờ học tập. Hãy đặt vé trước để có chỗ ngồi đẹp và thoải mái hơn. Đừng quên chia sẻ cảm nhận sau khi xem phim nhé.", 
     "label": "entertainment"},

    {"subject": "Nhạc hot tuần này", 
     "body": "Danh sách nhạc hot tuần này đã được cập nhật trên các nền tảng trực tuyến. Hãy dành thời gian nghe thử để thư giãn sau những giờ làm việc. Nếu có bài hát nào hay, hãy giới thiệu cho bạn bè để cùng thưởng thức. Âm nhạc sẽ giúp cuộc sống thêm phần thú vị hơn.", 
     "label": "entertainment"},

    {"subject": "Sự kiện lớn", 
     "body": "Sự kiện giải trí lớn nhất năm sẽ diễn ra vào tháng tới tại trung tâm thành phố. Rất nhiều hoạt động hấp dẫn và phần thưởng giá trị đang chờ đón bạn. Đăng ký sớm để nhận vé miễn phí và quà tặng đặc biệt. Hãy chuẩn bị tinh thần để trải nghiệm một sự kiện hoành tráng chưa từng có.", 
     "label": "entertainment"},

    {"subject": "Phim hành động mới", 
     "body": "Bộ phim hành động mới vừa ra mắt đã nhận được rất nhiều lời khen từ giới phê bình. Nếu bạn yêu thích thể loại này, chắc chắn đây sẽ là lựa chọn tuyệt vời. Rủ bạn bè cùng đi xem để có thêm những trải nghiệm thú vị. Đừng quên chia sẻ cảm nhận của bạn sau khi xem nhé.", 
     "label": "entertainment"},

    # Spam (5)
    {"subject": "Bạn đã trúng thưởng", 
     "body": "Click vào đường link để nhận thưởng ngay lập tức! Bạn là một trong số ít người may mắn được chọn. Giải thưởng giá trị lên đến 100 triệu đồng đang chờ bạn. Hãy điền thông tin cá nhân ngay để xác nhận quyền lợi của mình.", 
     "label": "spam"},

    {"subject": "Nhận tiền ngay", 
     "body": "Thông tin bí mật chỉ dành riêng cho bạn: cơ hội nhận tiền mặt cực lớn với một cú nhấp chuột. Hãy truy cập đường link bên dưới để biết thêm chi tiết. Đừng chia sẻ email này cho ai khác để giữ quyền lợi. Chúc bạn may mắn với cơ hội đổi đời này.", 
     "label": "spam"},

    {"subject": "Giải đặc biệt", 
     "body": "Bạn đã trúng thưởng giải đặc biệt từ chương trình khuyến mãi của chúng tôi. Vui lòng xác nhận thông tin cá nhân trong vòng 24 giờ để nhận giải. Nếu quá thời hạn, giải thưởng sẽ được trao cho người khác. Đừng bỏ lỡ cơ hội hiếm có này nhé.", 
     "label": "spam"},

    {"subject": "Tặng 5 triệu", 
     "body": "Nhận ngay 5 triệu đồng chỉ với vài bước đơn giản khi đăng ký tài khoản mới. Chương trình chỉ áp dụng cho 100 người đầu tiên nên bạn hãy nhanh tay. Đây là cơ hội hiếm có để sở hữu phần thưởng giá trị. Hãy làm theo hướng dẫn trong email này để nhận tiền ngay.", 
     "label": "spam"},

    {"subject": "Khuyến mãi sốc", 
     "body": "Khuyến mãi sốc chưa từng có: mua hàng không cần trả tiền trước. Bạn còn được tặng thêm nhiều quà hấp dẫn khi đăng ký ngay hôm nay. Số lượng có hạn nên ưu đãi chỉ dành cho khách hàng nhanh tay nhất. Hãy truy cập website của chúng tôi để nhận phần thưởng ngay.", 
     "label": "spam"}
]




edge_service = EdgeService(EdgeChromiumDriverManager().install())
edge_options = EdgeOptions()
driver = webdriver.Edge(service=edge_service, options=edge_options)
webbrowser.register('edge', None, webbrowser.BackgroundBrowser(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"))
webbrowser.get('edge').open('https://mail.google.com/')

input("Hãy đăng nhập Gmail thủ công rồi nhấn Enter để tiếp tục...")

for i in range(len(emails)):
    email = emails[i]
    label = email["label"]
    subject = email["subject"]
    body = email["body"]

    # Nhấn nút Soạn thư
    compose_btn = driver.find_element(By.CSS_SELECTOR, '.T-I.T-I-KE.L3')
    compose_btn.click()
    time.sleep(2)

    # Nhập email người nhận
    to_box = driver.find_element(By.NAME, 'to')
    to_box.send_keys('ming2005hn1@gmail.com')

    # Nhập tiêu đề
    subject_box = driver.find_element(By.NAME, 'subjectbox')
    subject_box.send_keys(f'[{label.upper()}] {subject}')

    # Nhập nội dung
    body_box = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Nội dung thư"]')
    body_box.send_keys(body)

    # Gửi thư
    send_btn = driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="Gửi"]')
    send_btn.click()

    print(f'Đã gửi email {i+1}: {label}')

    # Đợi ngẫu nhiên 30-60s
    wait_time = random.randint(30, 60)
    time.sleep(wait_time)

driver.quit()