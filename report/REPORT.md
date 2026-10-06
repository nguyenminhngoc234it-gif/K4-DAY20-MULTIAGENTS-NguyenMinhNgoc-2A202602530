# Báo cáo Lab: Self-evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Minh Ngọc | 2A202602530 | Cài đặt harness, chạy thí nghiệm, phân tích kết quả và hoàn thiện báo cáo (100%) |

- Mô hình: `openai:gpt-4.1-mini`; `LAB_TEMPERATURE=0`; `recursion_limit=60` (giá trị mặc định của runner).
- Deep Agents `0.7.21`; Microsoft Windows NT `10.0.26300.0`; chạy trực tiếp bằng `LocalShellBackend`, không dùng Docker.
- Số lần chạy tác vụ đã lưu: **21** (18 lượt chính thức và 3 lượt kiểm tra bộ skill curator vòng 1); tài liệu lab không nêu hạn mức số lượt cụ thể. Curator được gọi 2 lần.
- Commit của tag `freeze`: `4c8a19cdb1ebb8b222851eb55251d9050ad5b4c0`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán **baseline đạt điểm tác vụ đánh giá cao hơn subagents**. Trên tác vụ học, baseline đạt 12/27 check còn subagents chỉ đạt 6/27; tác tử chính đều gọi `general-purpose` đúng một lần nhưng lời giao việc thiếu ngữ cảnh và khâu kiểm tra kết quả yếu. Điều này phù hợp với đặc tính subagent là stateless và chỉ thấy prompt được giao: việc phân rã không tự cải thiện chất lượng nếu yêu cầu, tiêu chí nghiệm thu và bằng chứng cần trả về không được truyền đầy đủ.
- H2 (skills-auto so với baseline): Dự đoán **baseline đạt điểm tác vụ đánh giá cao hơn skills-auto**, dù skills-auto có tiềm năng hỗ trợ các check quy ước. Căn cứ là lỗi nhóm E chiếm 9/15 lỗi baseline và nội dung skill vòng 2 bao phủ nhiều quy ước tương ứng, nhưng trong lần kiểm tra trên tác vụ học cả ba lượt đều có `skills_read = 0`; skills-auto chỉ đạt 7/27 so với 12/27 của baseline. Vì skill chỉ có thể tác động khi được truy xuất và làm theo, bằng chứng hiện có chưa ủng hộ khả năng lợi ích đó chuyển sang tác vụ đánh giá.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán **điểm trung bình trên tác vụ đánh giá thấp hơn trên tác vụ học đối với cả ba điều kiện**, và mức giảm của skills-auto không nhỏ hơn baseline. Tác vụ đánh giá đòi hỏi chuyển giao sang dữ liệu/mã và các quy ước mới, trong khi chỉ có ba tác vụ học, mỗi cấu hình mới chạy một lần; các skill hiện tại còn bám vào một số quy ước đã thấy và chưa từng được agent đọc. Vì vậy, lợi thế nếu có trên tác vụ học khó tổng quát hóa, còn nhiễu giữa các lần chạy có thể tạo chênh lệch nhưng không nên được diễn giải là hiệu quả học.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; công cụ shell `execute`; và công cụ subagent `task`. Trong đó, `execute` cho phép chạy lệnh shell.
2. `task` mô tả `general-purpose` là subagent dùng để nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và thực hiện tác vụ nhiều bước; nó có cùng khả năng/công cụ như tác tử chính. Mặc định mỗi lần gọi là stateless: subagent chỉ thấy prompt (mô tả công việc) được giao, không thấy lịch sử hội thoại/ngữ cảnh của tác tử chính.
3. System prompt mặc định rỗng. Hướng dẫn từ `task`: “Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls.” Hướng dẫn từ `execute`: “Use read_file rather than cat/head/tail.”

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | G | `detail`: “the original files in tests/ must not be modified”. Tuy nhiên, trace chỉ **đọc** `tests/test_report.py`, không có lệnh ghi/sửa tệp test. Kiểm tra kho cho thấy tệp được checkout với `w/crlf`, trong khi checker băm byte thô theo hash LF; vì vậy đây là sai lệch môi trường dòng kết thúc, không phải hành vi sửa test của tác tử. |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function ... has type annotations on all parameters and on the return value.` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... (at least 3); the file must pass.` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md ... (at least 3 bullets).` |
| `data-learn` | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents`; tác tử ghi `north_q1_revenue: 3130.24` thay vì số cent nguyên. |
| `data-learn` | `rule_meta_block` | E | `RULE: answer.json has an object meta = {source, rows_in, rows_used}`; đầu ra chỉ có năm khóa nghiệp vụ. |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv ...`; trace không tạo `clean.csv`. |
| `logs-learn` | `entry_count` | D | `detail`: “wrong number of entries (got 20)”. Trace đọc log theo hai đoạn rồi chép thủ công JSON, không dùng một bộ phân tích/kiểm tra số bản ghi nên bỏ sót 5/25 mục. |
| `logs-learn` | `timestamps_utc` | D | `detail`: “17/25 timestamps match”; dữ liệu có nhiều múi giờ nhưng kết quả được chép thủ công, dẫn tới 8 timestamp sai. |
| `logs-learn` | `exception_fields` | D | `detail`: “8 wrong exception values”; tác tử không xử lý ổn định các traceback nhiều dòng để lấy dòng cuối. |
| `logs-learn` | `repeat_counts` | D | `detail`: “8 wrong repeat_count values”; các dòng `last message repeated N times` không được gắn đúng vào mục log trước đó. |
| `logs-learn` | `counts_by_service` | D | `detail`: “counts_by_service: wrong values”; đây là hệ quả của việc bỏ sót mục và tính sai `repeat_count`. |
| `logs-learn` | `rule_service_names` | E | `RULE: service names ... lower-case with '-' replaced by '_'`; trace vẫn ghi `inventory-service`, `auth-service`, v.v. |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E | `RULE: the top-level object has schema_version: 2 and generated_by: log-triage.` |

Tổng cộng, đường cơ sở đạt **12/18 check kỹ thuật** và **0/9 check quy ước**. Theo từng tác vụ, số check kỹ thuật đạt/tổng là `code-learn` **6/7**, `data-learn` **5/5**, `logs-learn` **1/6**. Đây là bằng chứng phủ định cho việc quy toàn bộ lỗi vào A-D: hai tác vụ đầu đạt 11/12 check kỹ thuật, còn các thất bại của chúng chủ yếu là quy ước ẩn.

Nhóm **E chiếm đa số với 9/15 check thất bại (60%)**, tiếp theo là D với 5/15 và G với 1/15; không có check nào được xếp vào A, B, C hoặc F. Một skill tổng quát có checklist “đọc quy ước dự án, chuẩn hóa schema/đơn vị, tạo artifact phụ, rồi tự kiểm tra trước khi kết thúc” có khả năng phòng ngừa phần lớn lỗi E. Skill cũng có thể giảm lỗi D nếu yêu cầu dùng parser thay vì chép tay và kiểm tra số bản ghi, múi giờ, traceback, repeat count. Tuy nhiên, skill không xử lý được lỗi G do khác biệt CRLF/LF của harness.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  - `explorer`: đọc README, docstring, dữ liệu/mã và báo cáo bằng chứng mà không sửa tệp; tách bước khám phá yêu cầu khỏi triển khai.
  - `implementer`: thực hiện một thay đổi đã được khoanh vùng và chạy test/script; dùng khi yêu cầu đã rõ và cần tạo artifact.
  - `reviewer`: kiểm tra độc lập kết quả theo đặc tả, test và edge case mà không sửa tệp; dùng để tránh tác tử chính tin báo cáo chưa kiểm chứng.

Trong cả ba tác vụ, tác tử chính không chọn ba subagent chuyên biệt trên mà gọi subagent mặc định `general-purpose` đúng **1 lần/tác vụ** (`subagent_calls = 1`). Vì vậy tổng cộng có 3 lần giao việc; không có trường hợp `subagent_calls = 0`.

| Tác vụ | Lời giao việc và cách kiểm tra kết quả |
|---|---|
| `code-learn` | Lời giao việc có yêu cầu sửa package, không sửa test và theo docstring, nhưng không truyền nội dung quy ước Acme, không yêu cầu đọc `workspace/README.md`, không nêu chính xác lệnh kiểm tra hay các artifact quy ước. Sau khi subagent báo đã sửa, tác tử chính đọc lại ba tệp nguồn và chạy `pytest`; đây là lần duy nhất có kiểm tra thực chất, dù pytest lỗi môi trường và tác tử không tìm cách kiểm tra thay thế. |
| `data-learn` | Lời giao việc nói sẽ đọc CSV/README và nêu tên các chỉ số, nhưng tham chiếu mơ hồ đến “user's requirements” mà subagent không nhìn thấy; thiếu khoảng thời gian UTC chính xác, schema đầu ra và nội dung quy ước Acme. Subagent chỉ báo kế hoạch, không trả con số và không xác nhận đã ghi tệp. Tác tử chính không đọc dữ liệu/README, không kiểm tra báo cáo mà ghi các giá trị mẫu không có bằng chứng (`123456.78`, `234`, `South`, `12`, `5`), dẫn tới 0/8 check. |
| `logs-learn` | Lời giao việc truyền khá đầy đủ quy tắc parse chính, nhưng nói “given JSON structure” mà không đưa cấu trúc đó và không truyền quy ước Acme/README cụ thể. Subagent tuyên bố đã ghi tệp; tác tử chính có đọc lại nhưng thấy ngay `{"entries":[],"counts_by_service":{}}` vẫn chấp nhận, không đối chiếu khóa bắt buộc `errors`, không đọc `app.log` và không chạy kiểm tra. Kết quả là 0/9 check. |

| Tác vụ | Baseline (token; giây; điểm) | Subagents (token; giây; điểm) | Thay đổi |
|---|---:|---:|---:|
| `code-learn` | 63.100; 23,2; 6/10 | 98.866; 50,5; 6/10 | +56,7% token, +117,7% thời gian; điểm không đổi |
| `data-learn` | 120.417; 41,4; 5/8 | 19.640; 11,5; 0/8 | -83,7% token, -72,2% thời gian; mất 5 check đạt |
| `logs-learn` | 21.489; 13,1; 1/9 | 20.500; 9,7; 0/9 | -4,6% token, -26,0% thời gian; mất 1 check đạt |
| **Tổng** | **205.006; 77,7; 12/27** | **139.006; 71,7; 6/27** | **-32,2% token, -7,7% thời gian; số check đạt giảm một nửa** |

Theo `scripts/check_breakdown.py`, token trung bình giảm từ **68.335** (`baseline`) xuống **46.335** (`subagents`), tương ứng giảm 32,2%; cả hai điều kiện đều có `read a skill = 0/3`, đúng với giai đoạn chưa dùng skill.

Điều kiện `subagents` không cho thấy cải thiện chất lượng. Mức token thấp hơn ở tổng thể chủ yếu do `data-learn` và `logs-learn` kết thúc sớm với đầu ra thiếu/sai, nên không thể diễn giải là tăng hiệu quả. Vấn đề chính không phải thiếu subagent mà là chọn `general-purpose`, giao thiếu ngữ cảnh và không thực hiện yêu cầu “check what a subagent returns before you rely on it”.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Curator được chạy **2 lần** (mức tối đa cho phép). Lần 1 sinh 3 skill hợp lệ nhưng cả ba tác vụ đều có `skills_read = 0`; điều kiện `skills-auto` đạt lần lượt `code-learn` 6/10, `data-learn` 4/8 và `logs-learn` 1/9. Nhóm xóa cả 3 skill vòng 1 và chạy lại vì `description` không kích hoạt được việc đọc skill; riêng `follow-logging-and-error-reporting-conventions` còn quá hẹp cho log và không bao phủ lỗi dữ liệu.
- Lần 2 sinh 3 skill hợp lệ bên dưới. Không skill nào nhắc định danh tác vụ đánh giá và `validate_skill` trả về danh sách lỗi rỗng cho cả ba. Nhóm giữ nguyên đầu ra, không sửa tay.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `enforce-type-annotations-on-public-functions` | Khá tổng quát cho thay đổi API Python; không nêu tên tệp, hàm hay đáp án của tác vụ học. | Hướng dẫn đúng với phản hồi `rule_type_hints`: kiểm tra tham số và kiểu trả về, chạy static checker nếu có. Quy ước “hàm public là tên không bắt đầu `_`” là heuristic, không đúng tuyệt đối cho mọi dự án, nhưng không gây hại trong bối cảnh lab. | **12 dòng**; `description` bắt đầu bằng “Use this skill when...” và nêu đúng tình huống sửa hàm public. `code-learn` không đọc skill (`skills_read = 0`), nên `rule_type_hints` vẫn thất bại. |
| `follow-project-conventions-for-data-formatting-and-logging` | Tổng quát hóa sang hai nhóm xuất dữ liệu và phân tích log, nhưng còn bám sát các quy ước Acme đã thấy như cent nguyên, metadata và tên service; vì vậy có nguy cơ quá khớp. | Các quy tắc khớp phản hồi grader: chuẩn hóa, loại trùng, UTC, schema, sắp xếp và kiểm tra đầu ra. Chỉ dẫn “luôn đổi tiền sang cent” có thể sai ngoài dự án có quy ước này; bước 1 yêu cầu đọc quy ước dự án giúp giảm rủi ro nhưng không loại bỏ hoàn toàn. | **16 dòng**; `description` rộng và nêu đúng lúc tạo output/log. Cả `data-learn` và `logs-learn` đều không đọc skill (`skills_read = 0`). |
| `maintain-test-suite-integrity-and-regression-coverage` | Tổng quát cho sửa lỗi/thêm tính năng; tên `tests/test_regressions.py` là quy ước Acme được phép, không phải rò rỉ tác vụ đánh giá. | Đúng với `tests_not_modified` và `rule_regression_tests`: không sửa test cũ, thêm regression test và chạy toàn bộ suite. Mệnh đề “never modify existing tests” không phải quy tắc phổ quát cho mọi kho, nhưng phù hợp tình huống kích hoạt đã ghi trong `description`. | **12 dòng**; `description` rõ khi sửa bug/thêm tính năng. `code-learn` không đọc skill (`skills_read = 0`), nên check regression vẫn thất bại. |

Kết quả Phần 3.4 với bộ skill vòng 2 là `code-learn` **6/10**, `data-learn` **0/8**, `logs-learn` **1/9**; tổng **7/27**, so với baseline **12/27**. Cả ba lần chạy có `skills_read = 0`, `skills_modified = false` và `error = null`. Do skill không được đọc, không thể quy chênh lệch điểm cho nội dung skill. Bằng chứng rõ nhất là `data-learn`: trace cho thấy agent chỉ đọc 40/102 dòng CSV rồi ghi ngay `answer.json`, dẫn tới 0/8; đây là lỗi quy trình/dao động của lần chạy, không phải bằng chứng skill gây hại. Kết quả vòng 1 được lưu tại `results/skills-auto-curator1/` để đối chiếu.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng do `python -m lab.compare` sinh trong `report/table.md`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 0/8 | 0/8 |
| logs-learn | 1/9 | 0/9 | 1/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 5/9 | 1/9 | 5/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.45 | 0.20 | 0.24 |
| **Mean score - evaluation tasks** | 0.40 | 0.25 | 0.40 |
| **Mean tokens per run** | 71,198 | 47,316 | 46,624 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Phân rã check theo logic của `scripts/check_breakdown.py`:

| Điều kiện | Vai trò | Check kỹ thuật | Check quy ước | Token trung bình | Lượt đọc skill |
|---|---|---:|---:|---:|---:|
| `baseline` | learn | 12/18 | 0/9 | 68.335 | 0/3 |
| `baseline` | eval | 12/18 | 0/12 | 74.060 | 0/3 |
| `subagents` | learn | 6/18 | 0/9 | 46.335 | 0/3 |
| `subagents` | eval | 8/18 | 0/12 | 48.297 | 0/3 |
| `skills-auto` | learn | 7/18 | 0/9 | 34.095 | 0/3 |
| `skills-auto` | eval | 12/18 | 0/12 | 59.154 | 0/3 |

Cả 18 lượt chạy chính thức đều có `error = null` và `skills_modified = false`; không có lượt nào phải chạy lại vì lỗi. Sáu lượt `skills-auto` dùng cùng hash skill `9431831124701adfa787fee7e8a62e5524af0017bc9277f33305c923d38a5bf8`. Commit `hypotheses` (`8531ca9`) đứng trước tag `freeze`, và `skills/` không khác so với tag.

## 8. Phân tích

1. **So sánh điểm.** Trên tác vụ học, không điều kiện nào cải thiện baseline: `subagents` đạt 0,20, giảm 0,25 điểm trung bình; `skills-auto` đạt 0,24, giảm 0,21 so với 0,45. Trên tác vụ đánh giá, `subagents` đạt 0,25, thấp hơn baseline 0,15; `skills-auto` bằng baseline ở 0,40, không phải là cải thiện. Vì không có điều kiện nào cải thiện tác vụ học nên không xuất hiện mẫu “tăng trên learn nhưng không tăng trên eval”. H1 được ủng hộ; H2 không được ủng hộ vì baseline và skills-auto hòa nhau; H3 chỉ đúng với baseline (0,45 xuống 0,40), còn `subagents` tăng 0,20 lên 0,25 và `skills-auto` tăng 0,24 lên 0,40. Các đảo chiều này cho thấy độ khó giữa hai nhóm tác vụ và nhiễu lần chạy ảnh hưởng mạnh hơn cơ chế học quan sát được.

2. **Check kỹ thuật và quy ước.** Baseline đạt 12/18 check kỹ thuật ở cả learn và eval nhưng 0/9 và 0/12 check quy ước. `skills-auto` đạt lần lượt 7/18 và 12/18 check kỹ thuật, đồng thời vẫn đạt **0 check quy ước** ở cả hai vai trò. Do đó skill sinh ra chưa giúp được nhóm nào một cách có thể quy thuộc. Ba quy ước mới của eval là `rule_version_bump`, `rule_sorted_keys_format` và `rule_source_line`; cả ba đều thất bại ở `skills-auto`. Nguyên nhân trực tiếp là cả sáu lượt có `skills_read = 0`; ngoài ra nội dung skill đóng băng cũng không nêu ba quy ước mới này, nên ngay cả khi được đọc thì khả năng chuyển giao vẫn chưa được bảo đảm.

3. **Đối chiếu vết và việc đọc skill.** Không có check nào có thể khẳng định là “được skill giúp đạt”: chẳng hạn `duplicate_events_removed` của `data-eval` đạt ở cả baseline và `skills-auto`, trong khi trace `skills-auto` không có lần đọc `SKILL.md`; kết quả này đến từ việc agent tự viết và chạy `analyze_orders.py`, không phải bằng chứng về hiệu quả skill. Ngược lại, `rule_type_hints` là ví dụ skill không giúp: skill `enforce-type-annotations-on-public-functions` chứa đúng hướng dẫn liên quan nhưng `code-eval` có `skills_read = 0`, và check vẫn thất bại. Tương tự, các skill về định dạng dữ liệu/log và regression test đều không thể tác động khi bước truy xuất đầu tiên không xảy ra.

4. **Chi phí và hiệu quả.** Token trung bình trên toàn bộ sáu lượt là 71.198 cho baseline, 47.316 cho `subagents` và 46.624 cho `skills-auto`. Tính theo tổng check đạt trên tổng token, baseline đạt 24 check/427.188 token, tương đương **56,2 check/triệu token**; `subagents` đạt 14/283.898, tương đương **49,3 check/triệu token**; `skills-auto` đạt 19/279.749, tương đương **67,9 check/triệu token**. `skills-auto` có tỷ lệ điểm/token cao nhất nhưng không thể coi đây là lợi ích của skill vì không lượt nào đọc skill; mức token thấp còn gắn với `data-learn` kết thúc sau 4 giây và đạt 0/8. Đa tác tử không đáng chi phí trong thí nghiệm này: điểm thấp hơn baseline ở cả hai vai trò, hiệu quả token thấp nhất, và riêng `code-learn` dùng 98.866 token so với 63.100 của baseline mà cùng đạt 6/10.

5. **Rò rỉ và quá khớp.** Không thấy rò rỉ trực tiếp: skill không chứa tên/định danh riêng của tác vụ đánh giá, curator chỉ nhận phản hồi và trace của tác vụ học, mọi lượt dùng đúng hash đã đóng băng, và `skills_modified = false`. Tuy nhiên có dấu hiệu quá khớp nhẹ ở nội dung như tiền luôn đổi sang cent, schema metadata, chuẩn hóa tên service và tên cố định `tests/test_regressions.py`; đây là các quy ước đã thấy trong learn chứ chưa phải nguyên tắc phổ quát. Nhóm giảm rủi ro bằng cách đánh giá thủ công, xóa bộ skill vòng 1 có mô tả kích hoạt kém, chạy curator tối đa hai lần, không sửa tay đầu ra vòng 2 và đóng băng skill trước khi xem điểm eval.

6. **Nhiễu.** Với cùng bộ skill vòng 2, Phần 3.4 ghi nhận `code-learn` 6/10, `data-learn` 0/8 và `logs-learn` 1/9, tổng **7/27**; sau đóng băng ba kết quả tương ứng vẫn là 6/10, 0/8 và 1/9, nên chênh lệch quan sát được là **0 check**. Riêng bộ skill curator vòng 1 từng đạt 11/27 nhưng đó là bộ skill khác, không dùng để ước lượng nhiễu của bộ đóng băng. Quan sát bằng 0 không chứng minh hệ thống tất định: mỗi cấu hình chỉ có một cặp quan sát, còn chênh lệch lớn giữa baseline và các lần chạy khác vẫn có thể do hành vi mô hình, kết thúc sớm và việc đọc thiếu dữ liệu. Vì vậy các chênh lệch một lần chạy trong bảng chỉ là bằng chứng mô tả, chưa đủ cho kết luận nhân quả.

## 9. Hạn chế và tính hợp lệ

1. **Mẫu nhỏ:** chỉ có ba tác vụ học và ba tác vụ đánh giá. Một tác vụ `data-*` hoặc `logs-*` thất bại có thể dịch chuyển mạnh điểm trung bình, nên kết luận khó tổng quát sang các kho mã và dạng dữ liệu khác.
2. **Mỗi cấu hình chỉ chạy chính thức một lần:** không có trung bình qua nhiều seed/lần lặp hoặc khoảng tin cậy. Vì thế không tách được hiệu ứng điều kiện khỏi biến thiên ngẫu nhiên của mô hình.
3. **Không có treatment thực tế cho skill:** `skills_read = 0/6` ở `skills-auto`. Thí nghiệm chỉ đánh giá cấu hình có skill nhưng không đánh giá được tác động của việc đọc và làm theo skill; kết quả hòa baseline trên eval không phải bằng chứng skill hiệu quả.
4. **Một mô hình và một cấu hình:** mọi lượt dùng `gpt-4.1-mini`, nhiệt độ 0 và recursion limit 60. Kết luận về subagent, khả năng chọn skill và chi phí token có thể thay đổi với mô hình hoặc giới hạn khác.
5. **Tác vụ và quy ước do lab thiết kế:** nhiều check `rule_` cố ý ẩn khỏi đề và lặp lại kiểu quy ước Acme. Điều này thuận lợi để đo self-evolving nhưng có thể làm skill quá khớp, không đại diện đầy đủ cho quy ước dự án thực tế.
6. **Sai lệch môi trường:** `tests_not_modified` thất bại do khác biệt CRLF/LF và lệnh `pytest` trong một số trace lỗi vì môi trường Python bị hỏng. Các lỗi hạ tầng này làm giảm điểm hoặc giảm mức kiểm chứng mà không phản ánh hoàn toàn năng lực sửa mã.

## 10. Kết luận

Baseline đạt điểm cao nhất trên tác vụ học (0,45) và đồng hạng cao nhất với `skills-auto` trên tác vụ đánh giá (0,40). `Subagents` không cải thiện chất lượng hay hiệu quả token; nguyên nhân quan sát được là giao việc thiếu ngữ cảnh và kiểm tra đầu ra yếu. Bộ skill đóng băng không tạo được hiệu ứng đo lường vì cả sáu lượt đều có `skills_read = 0`, dù `skills-auto` có tỷ lệ check/token cao nhất. Kết quả hiện tại chỉ hỗ trợ kết luận mô tả, không hỗ trợ quan hệ nhân quả do mẫu nhỏ và mỗi cấu hình chạy một lần. Bước tiếp theo nên sửa cơ chế mô tả/truy xuất để bảo đảm agent đọc skill phù hợp, rồi lặp mỗi điều kiện ít nhất ba lần và báo cáo trung bình cùng khoảng dao động.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): `pytest tests/test_01_provided.py`; `python scripts/tour.py`; các test `test_02_agent.py`, `test_03_runner.py`, `test_04_curator.py`; `python -m lab.runner --condition baseline --tasks learn`; `python -m lab.runner --condition subagents --tasks learn`; `python -m lab.curator` (2 lần); `python -m lab.runner --condition skills-auto --tasks learn`; commit `hypotheses`; tạo tag `freeze`; chạy `baseline --tasks eval`, `subagents --tasks eval`, `skills-auto --tasks all`; `python -m lab.compare`; `python scripts/check_breakdown.py`; `python scripts/verify_freeze.py`.
- Thử thách mở rộng: không thực hiện.
- Ghi chú khác: `report/table.md` là bảng sinh tự động; các số phân rã trong mục 7 được tính trực tiếp từ `checks` và `tokens.total` của 18 `run.json` chính thức.
