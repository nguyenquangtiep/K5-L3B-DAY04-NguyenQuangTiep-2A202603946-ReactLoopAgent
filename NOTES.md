# Ghi chú phân tích · Day 04

Họ và tên: Nguyễn Quang Tiệp
MSSV: 2A202603946

## 1. Case được chọn

- ID case: A5
- Yêu cầu của người dùng: "Tôi cần danh sách đầy đủ tất cả incident GitHub Actions trong năm 2025. Hãy tìm dữ liệu và nói rõ độ đầy đủ của kết quả, đừng bịa."
- Câu trả lời của agent: “hiện tại không có incident nào liên quan đến GitHub Actions trong năm 2025 được ghi nhận”.
- Agent còn ghi "Tổng số incident liên quan: 5" và liệt kê các incident có thời gian cập nhật trong tháng 11/2026.
- Điểm ở lần chạy 1: 55/100.

Tôi chọn case này vì câu hỏi yêu cầu dữ liệu đầy đủ cho năm 2025, trong khi công cụ chỉ cung cấp một phần lịch sử gần nhất. Agent cần nói rõ không đủ dữ liệu để đáp ứng yêu cầu, thay vì kết luận về toàn bộ năm 2025. Đây là lỗi diễn giải giới hạn bằng chứng; chương trình vẫn chạy xong và trả status completed.

## 2. Bằng chứng trong trace

Đoạn trace của case A5 trong eval_before.json. Trace ghi dữ liệu công cụ đã trả về; đối chiếu dữ liệu này với câu trả lời ở mục 1 cho thấy lỗi diễn giải của agent:
```
"trace": [
          {
            "event": "model",
            "step": 1,
            "finish": "tool_calls"
          },
          {
            "event": "tool",
            "step": 1,
            "name": "get_status",
            "arguments": {
              "provider": "github",
              "component": "actions"
            },
            "result": {
              "provider": "github",
              "captured_at": "2026-11-09T03:50:47.065020+00:00",
              "overall": {
                "indicator": "none",
                "description": "All Systems Operational"
              },
              "components": [
                {
                  "name": "Actions",
                  "status": "operational"
                }
              ],
              "incidents": [
                {
                  "id": "pfbmpxxfq1cy",
                  "name": "Degraded performance for multiple GitHub services",
                  "status": "resolved",
                  "updated_at": "2026-11-06T00:20:49.369Z"
                },
                {
                  "id": "t89g2q1800fr",
                  "name": "Incident with Actions",
                  "status": "resolved",
                  "updated_at": "2026-11-05T17:42:35.455Z"
                },
                {
                  "id": "h02n9572mx9y",
                  "name": "Incident with Actions",
                  "status": "resolved",
                  "updated_at": "2026-11-07T01:10:18.506Z"
                },
                {
                  "id": "xr3myzj7ms51",
                  "name": "Incident with Actions and Pages",
                  "status": "resolved",
                  "updated_at": "2026-11-07T01:04:38.647Z"
                },
                {
                  "id": "smtdswd1h2w4",
                  "name": "Incident with Pull Requests, Git Operations and Issues",
                  "status": "resolved",
                  "updated_at": "2026-11-04T11:50:06.459Z"
                }
              ],
              "matching_incidents_in_last_50": 23,
              "note": "Chỉ tìm theo chuỗi trong 50 incident gần nhất; không tìm thấy không chứng minh không có sự cố.",
              "source": "https://www.githubstatus.com"
            }
          },
          {
            "event": "model",
            "step": 2,
            "finish": "stop"
          }
        ]

```
Các bằng chứng cụ thể:

- Agent gọi get_status với provider=github và component=actions. Công cụ này tìm theo chuỗi trong 50 incident gần nhất, không truy vấn toàn bộ lịch sử năm 2025.
- captured_at là 2026-11-09T03:50:47.065020+00:00. Đây là thời điểm lưu snapshot, không phải thời điểm kiểm tra trạng thái trực tiếp.
- Danh sách incidents hiển thị 5 mục, có updated_at trong tháng 11/2026. Dữ liệu này không đủ để kết luận về toàn bộ năm 2025.
- matching_incidents_in_last_50 bằng 23. Do đó, 5 là số mục hiển thị, còn 23 là số incident khớp trong phạm vi tìm kiếm; cả hai đều không phải tổng số incident năm 2025.
- Trường note đã cảnh báo: "Chỉ tìm theo chuỗi trong 50 incident gần nhất; không tìm thấy không chứng minh không có sự cố."

Nguyên nhân có thể: agent chưa áp dụng đúng giới hạn dữ liệu dù đã nhận cảnh báo từ tool. Agent nhầm việc không quan sát thấy incident năm 2025 với bằng chứng rằng năm đó không có incident, đồng thời nhầm số mục hiển thị với số mục khớp. SYSTEM_PROMPT ban đầu có yêu cầu chung về giới hạn bằng chứng nhưng chưa hướng dẫn cụ thể cách xử lý yêu cầu thống kê đầy đủ theo năm.

Hành vi mong muốn: trả lời rằng snapshot hiện có không đủ để lập danh sách đầy đủ cho năm 2025; không khẳng định năm đó không có sự cố. Nếu đề cập số lượng, phải phân biệt 5 mục hiển thị với 23 mục khớp trong 50 incident gần nhất.

## 3. Thay đổi đã thực hiện

- Sửa gì, ở đâu: bổ sung hướng dẫn trong SYSTEM_PROMPT của agent.py về phạm vi thời gian, cách đọc số lượng incident và thời điểm snapshot.
- Với yêu cầu danh sách đầy đủ theo khoảng thời gian: yêu cầu agent kiểm tra dữ liệu có bao phủ khoảng thời gian đó không; nếu không đủ thì nêu rõ giới hạn, không suy ra rằng không có sự cố.
- Với số lượng: yêu cầu phân biệt số mục trong danh sách incidents với matching_incidents_in_last_50, không dùng số mục hiển thị làm tổng số incident khớp.
- Với thời gian: yêu cầu gắn nhận định trạng thái với captured_at, không gọi trạng thái trong snapshot là trạng thái hiện tại.
- Vì sao chọn thay đổi này: trace cho thấy công cụ đã trả cảnh báo và số lượng khớp, nên thay đổi tập trung vào cách agent diễn giải dữ liệu. Không cần thay đổi dữ liệu hoặc bộ chấm để xử lý lỗi này.

Ngoài thay đổi prompt, tôi bổ sung kiểm tra URL nguồn trong run_agent: lưu URL từ get_incident_details thành công vào incident_urls; nếu câu trả lời không chứa ít nhất một URL đã quan sát, ghi validation_missing_source và yêu cầu model sửa trong max_steps. Nếu hết lượt mà vẫn thiếu nguồn thì trả max_steps; không bắt buộc URL nếu không đọc incident thành công. Cơ chế này không trực tiếp giải quyết lỗi thời gian của A5 mà đáp ứng yêu cầu kiểm tra nguồn của bài.

Bộ kiểm tra offline sau thay đổi đạt 37/37 test, bao gồm các test yêu cầu sửa câu trả lời thiếu URL và không báo completed khi đã hết lượt mà chưa có nguồn. Trong eval_after.json, case H6 có một event validation_missing_source và kết thúc completed. Điều này cho thấy cơ chế nhắc sửa đã được kích hoạt, không chứng minh toàn bộ nội dung trả lời đúng.

## 4. So sánh hai lần chạy

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---|---|
| Điểm tổng | 80,68/100 | 76,36/100 |
| Case đã được chấm | 22/22 | 22/22 |
| Điểm case đã chọn | A5: 55/100 | A5: 75/100 |
| Số model calls của agent | 51 | 47 |
| Token của agent | 41.828 | 42.068 |
| Chi phí agent (USD, theo usage) | 0,01061505 | 0,00990015 |
| Token của judge | 40.641 | 33.263 |
| Chi phí judge (USD, theo usage) | 0,00757395 | 0,00634800 |
| Tổng chi phí agent và judge (USD) | 0,01818900 | 0,01624815 |

Hai file có cùng config: provider và judge_provider là openrouter; model và judge_model là openai/gpt-4o-mini; max_steps=8; dataset=core. Cả hai lần dùng snapshot của bộ eval. Số model calls trong bảng được đếm từ các phần tử usage của agent; token và chi phí được cộng riêng cho agent và judge trên toàn bộ 22 case, không bao gồm lần chạy thử E2.

- Phần cải thiện trong A5: điểm tăng 20 điểm. Câu trả lời sau sửa nêu rõ: "Tôi không thể cung cấp danh sách đầy đủ các sự cố trong năm 2025 vì dữ liệu không bao phủ khoảng thời gian đó." Agent cũng giải thích không thấy sự cố năm 2025 không có nghĩa năm đó không xảy ra sự cố. Đây là cải thiện quan sát được trong lần chạy này.
- Lỗi A5 còn lại: agent vẫn nói "Hiện tại, GitHub Actions đang hoạt động bình thường" dù dùng snapshot; vẫn ghi "Có tổng cộng 5 sự cố gần đây" thay vì phân biệt 5 mục hiển thị với 23 mục khớp. Vì vậy chưa thể coi A5 đã được sửa hoàn toàn.
- Điểm tổng giảm 4,32 điểm dù A5 cải thiện. Một số case giảm mạnh: E1 từ 75 xuống 45, H2 từ 100 xuống 50, H6 từ 60 xuống 45 và H7 từ 65 xuống 35. Một số case tăng, như E3 từ 75 lên 95 và A2 từ 80 lên 100.
- Theo nhận xét của judge, các điểm cần kiểm tra tiếp gồm phân biệt incident lịch sử với sự cố hiện tại ở E1, đọc đủ bằng chứng và tránh gộp incident ở H6, xử lý thiếu dữ liệu Cloudflare ở H7. Nhận xét này cần được đối chiếu với trace, không tự coi là kết luận đúng tuyệt đối.
- Kết luận từ hai lần chạy: thay đổi giúp A5 thể hiện giới hạn dữ liệu rõ hơn và bổ sung kiểm tra nguồn bằng code, nhưng chưa cho thấy chất lượng tổng thể tốt hơn. Số model calls giảm 4, token agent tăng 240; tổng chi phí ghi nhận giảm khoảng 0,00194 USD. Chưa đủ bằng chứng quy toàn bộ biến động cho thay đổi prompt hoặc validation.

## 5. Giới hạn

- LLM judge có thể chấm sai hoặc thiếu nhất quán. Điểm cần được đối chiếu với expected, câu trả lời và trace. Điểm eval không tự động bằng điểm bài lab.
- Trong lần eval đầu, agent và judge đều dùng openai/gpt-4o-mini qua OpenRouter. Việc cùng model tạo câu trả lời và chấm điểm có thể gây thiên lệch.
- Snapshot GitHub được lưu ngày 09/11/2026 và chỉ chứa phạm vi lịch sử giới hạn. Nó không chứng minh trạng thái dịch vụ hiện tại hoặc cung cấp thống kê đầy đủ cho năm 2025.
- Một lần chạy trước và một lần chạy sau chưa chứng minh độ ổn định do model có thể tạo câu trả lời khác nhau giữa các lần gọi. Chênh lệch điểm không nhất thiết hoàn toàn do thay đổi prompt.
- Khi chạy eval lần hai, cần giữ nguyên agent model, judge model, snapshot, max_steps và dataset để so sánh công bằng.
- Nhắc model trong prompt không tương đương với kiểm tra bắt buộc bằng code. Kiểm tra sự hiện diện của URL nguồn cũng không chứng minh mọi nhận định trong câu trả lời đều đúng.
