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

Tôi đã thực hiện nhiều vòng cải tiến trên agent.py. Không thay đổi fixtures, câu hỏi, scenarios, expected, rubric hoặc bộ chấm; không sửa tay điểm hay câu trả lời trong các file eval.

- Prompt: hướng dẫn chọn đúng loại công cụ, phân biệt trạng thái dịch vụ với incident, đọc incident liên quan khi cần nguyên nhân, xử lý timeout và nêu giới hạn snapshot.
- Kiểm tra nguồn: lưu URL incident đọc thành công. Nếu câu trả lời không chứa ít nhất một URL đã quan sát, ghi validation_missing_source và yêu cầu sửa trong max_steps. Hết lượt mà chưa đáp ứng thì không báo completed.
- Bổ sung evidence_observation: tạo bản sao kết quả tool để gửi cho model, kèm _agent_evidence về thời điểm snapshot, số incident hiển thị, số incident khớp, số update nhận được và dấu hiệu dữ liệu không đầy đủ. Kết quả gốc vẫn được giữ trong trace. Các số liệu được tính từ kết quả thực, không lấy từ expected.
- Bổ sung related_incidents: lấy ID từ URL incident GitHub/Cloudflare thực sự xuất hiện trong update. Chỉ nhận host được hỗ trợ, không hard-code ID theo case.
- Khi câu hỏi cần nguyên nhân hoặc theo liên kết, theo dõi các incident liên quan chưa kiểm tra. Nếu model định trả lời khi còn liên kết chưa đọc, ghi validation_unread_reference và yêu cầu gọi công cụ tiếp trong max_steps. Một liên kết đã thử nhưng lỗi không bị yêu cầu thử vô hạn. Cơ chế dùng từ khóa nhận diện yêu cầu nên chưa bao phủ mọi cách diễn đạt.
- Giữ khả năng nhận schemas và system_prompt riêng của BonusTools. Việc này chỉ chứng minh khả năng kết nối công cụ bonus, không chứng minh hoàn thành toàn bộ bonus.

Vì sao chọn các thay đổi này: A5 nhầm giới hạn dữ liệu và số lượng; H1/H6 từng bỏ qua incident được nguồn dẫn tới. Nhắc bằng prompt chưa đủ ổn định, nên tôi bổ sung dữ liệu tóm tắt có cấu trúc và kiểm tra việc đọc liên kết bằng code.

Kiểm tra offline: 40/40 tests trong tests/ và 3/3 tests trong bonus/ đạt. Ba test mới trong tests/test_evidence.py kiểm tra phân biệt số mục hiển thị/số khớp, không làm thay đổi kết quả gốc, chỉ nhận liên kết incident từ host được hỗ trợ và ngăn hoàn thành khi còn liên kết cần đọc ở giới hạn bước.

## 4. So sánh hai lần chạy

Bảng chính so sánh baseline ban đầu với phiên bản cải tiến mới nhất, cũng là kết quả cao nhất trong các lần eval đầy đủ được lưu hiện có.

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---|---|
| Điểm tổng | 80,68/100 | 83,41/100 |
| Case đã được chấm | 22/22 | 22/22 |
| Điểm case đã chọn | A5: 55/100 | A5: 90/100 |
| Số model calls của agent | 51 | 53 |
| Token của agent | 41.828 | 92.454 |
| Chi phí agent (USD, theo usage) | 0,01061505 | 0,01702755 |
| Token của judge | 40.641 | 41.010 |
| Chi phí judge (USD, theo usage) | 0,00757395 | 0,00749790 |
| Tổng chi phí agent và judge (USD) | 0,01818900 | 0,02452545 |

Hai file có cùng config: provider và judge_provider là openrouter; model và judge_model là openai/gpt-4o-mini; max_steps=8; dataset=core. Cả hai dùng snapshot của bộ eval. Số model calls được đếm bằng số phần tử usage của agent. Token và chi phí được cộng riêng cho agent/judge trên 22 case; không bao gồm chi phí các lần thử khác.

Lịch sử các vòng đánh giá được giữ lại:

| Lần đánh giá | File kết quả | Điểm |
|---|---|---|
| Baseline trước cải tiến | eval_before.json | 80,68 |
| Cải tiến đầu: prompt giới hạn dữ liệu và kiểm tra nguồn | eval_after_previous.json | 76,36 |
| Thử prompt quy trình chi tiết | eval_prompt_check.json | 77,27 |
| Bổ sung observation có cấu trúc và kiểm tra liên kết | eval_improved.json | 83,41 |

eval_after.json là bản sao nguyên vẹn của eval_improved.json do runner tạo. Kết quả after cũ được lưu thành eval_after_previous.json trước khi thay thế. Tôi không lấy điểm từng case từ các lần chạy khác nhau để ghép thành kết quả mới.

Kết quả cải thiện có bằng chứng:

- Điểm tổng tăng 2,73 điểm so với baseline, tăng 7,05 điểm so với bản after đầu và tăng 6,14 điểm so với lần thử prompt.
- A5 tăng 55 lên 90. Câu trả lời mới nêu: “điều này không đủ để khẳng định rằng không có incident nào trong năm 2025. Do đó, không thể lập danh sách đầy đủ cho năm 2025.” Agent phân biệt 5 mục hiển thị và 23 mục khớp, dù cách nói “có tối đa 23” vẫn chưa thật chính xác vì tool báo đúng 23 mục khớp.
- H1 tăng 60 lên 80 so với baseline. Trace cho thấy đã đọc incident ban đầu, incident Cloudflare và incident GitHub liên quan trong 2 model steps có tool call. Câu trả lời đã nêu nguyên nhân thay đổi cấu hình từ bản tổng kết.
- H6 tăng 60 lên 75 so với baseline, và từ 45 lên 75 so với after đầu. Trace có lời gọi đọc incident liên quan; agent trả lời nguyên nhân và nhắc chỉ nhận 3 trong 9 update.
- H2 đạt 100; trace có cả kiểm tra status và đọc chi tiết incident.

Lỗi còn lại và đánh đổi:

- H7 chỉ đạt 60, thấp hơn baseline 65. Agent nhận timeout Cloudflare và thừa nhận chưa xác minh được, nhưng vẫn viết “theo yêu cầu bạn ... operational”. Hướng dẫn và metadata chưa đủ ngăn việc chiều theo yêu cầu bịa. Đây là lỗi thật chưa được giải quyết.
- H8 đạt 70: agent truyền chuỗi khoảng năm vào incident_id thay vì kiểm tra status phù hợp, rồi diễn giải thiếu dữ liệu chưa chính xác. Cần cải thiện chọn công cụ/tham số cho yêu cầu thống kê dài hạn.
- E1 đạt 60 so với baseline 75; A1 đạt 75 so với baseline 100. Vì vậy không thể nói mọi case đều tốt hơn.
- H1 còn thiếu dẫn nguồn Cloudflare trong phần trả lời và thiếu cảnh báo nội dung bị cắt; H6 tập trung vào incident gộp nhưng chưa trả lời đầy đủ phần trạng thái Actions và incident ban đầu. Đọc thêm bằng chứng chưa bảo đảm model trình bày đủ.
- Số model calls tăng 2; token agent tăng 50.626; tổng chi phí agent và judge tăng khoảng 0,00634 USD so với baseline. Việc gửi thêm hướng dẫn và metadata, giữ lịch sử và đọc thêm incident có chi phí.
- Chất lượng được cải thiện trong lần đo mới nhưng vẫn còn lỗi đáng kể. Không thể quy toàn bộ thay đổi điểm cho một cơ chế vì đã thay đổi cả prompt và cách điều phối.

## 5. Giới hạn

- LLM judge có thể sai hoặc thiếu nhất quán. Cần đọc expected, trace và câu trả lời; điểm eval không tự động bằng điểm bài lab.
- Agent và judge đều dùng openai/gpt-4o-mini qua OpenRouter, có thể gây thiên lệch.
- Snapshot và phạm vi incident giới hạn không chứng minh trạng thái ngoài đời hiện tại hoặc lịch sử đầy đủ theo năm.
- Có nhiều vòng thử trên cùng bộ 22 case. Chọn kết quả cao nhất để báo cáo có thiên lệch lựa chọn; đây là kết quả phát triển trên bộ đã biết, không phải kiểm chứng trên dữ liệu độc lập.
- Mỗi phiên bản chưa được đánh giá lặp lại nhiều lần. Chênh lệch điểm có thể chịu ảnh hưởng bởi sự ngẫu nhiên của model và judge; chưa chứng minh độ ổn định hoặc bảo đảm lần chạy tiếp cũng đạt 83,41.
- Bộ tests offline không xác nhận mọi câu trả lời thực tế đúng. Metadata chỉ làm rõ dữ liệu đã có, không bổ sung bằng chứng bên ngoài.
- Kiểm tra URL chỉ xác nhận có ít nhất một URL đã quan sát, không bảo đảm mọi nhận định hoặc mọi provider đều được dẫn nguồn.
- Cơ chế theo liên kết chỉ nhận incident GitHub/Cloudflare theo định dạng được hỗ trợ và còn phụ thuộc cách diễn đạt câu hỏi; không phải trình duyệt đọc mọi URL.
- Chưa hoàn tất bộ eval bonus 10 case; các lần thử B2/B3 và 3 tests bonus không đủ để báo điểm bonus tổng.
