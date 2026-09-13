# AmazonHelp Intent Taxonomy

This document establishes the official intent taxonomy for **SupportPilot (AmazonHelp)**, derived from the empirical analysis of **20,000** clean, verified customer $\rightarrow$ brand support interactions in `data/sample/amazonhelp_conversations.csv`.

---

## 1. Intent Distribution Analysis

Preliminary discovery distribution across the 20,000-interaction sample:

| Intent Key | Display Name | Count | Percentage | Operational Role |
| :--- | :--- | :---: | :---: | :--- |
| `service_complaints_and_feedback` | **Service Complaints & Feedback** | 9,768 | 48.84% | Standard / Triage |
| `delivery_status_and_delay` | **Delivery Status & Delay** | 6,495 | 32.48% | Standard / Triage |
| `refund_inquiry` | **Refund Inquiry & Status** | 802 | 4.01% | Standard / Triage |
| `return_and_replacement` | **Return & Replacement Logistics** | 584 | 2.92% | Standard / Triage |
| `digital_services_and_device_support` | **Digital Services & Device Support** | 566 | 2.83% | Standard / Triage |
| `damaged_defective_or_wrong_item` | **Damaged, Defective, or Wrong Item** | 541 | 2.71% | Standard / Triage |
| `missing_package_false_delivery` | **Missing Package / False Delivery Status** | 387 | 1.93% | Standard / Triage |
| `prime_and_subscriptions` | **Prime & Subscription Management** | 332 | 1.66% | Standard / Triage |
| `account_access_and_security` | **Account Access & Security** | 322 | 1.61% | Standard / Triage |
| `payment_and_billing_issues` | **Payment & Billing Issues** | 102 | 0.51% | Standard / Triage |
| `order_cancellation_and_modification` | **Order Cancellation & Modification** | 101 | 0.51% | Standard / Triage |

*Total Interactions Analyzed: 20,000*

---

## 2. Intent Specifications

### `missing_package_false_delivery` — Missing Package / False Delivery Status

* **Empirical Volume**: 387 records (1.93%)
* **Definition**: Customer reports that tracking status indicates 'Delivered', 'handed to resident', or 'left in mailroom', but they have not received the parcel, suspect theft, or cannot locate it.
* **Boundary**: Applies strictly to cases where delivery was marked complete by the carrier but the item is missing. Standard shipping transit delays belong to 'delivery_status_and_delay'.
* **Confusing Intents**: delivery_status_and_delay, service_complaints_and_feedback
* **Typical Resolution**: AmazonHelp acknowledges the discrepancy, advises checking with neighbors/lockers, explains that carriers occasionally scan 24-36h prematurely, or escalates via secure phone/chat link for replacement/refund.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `646`): ".@AmazonHelp Item has not been delivered but tracking says it was handed to me over an hour ago... 2nd time this has happened. Sort it out https://t.co/42W82GcARk"
   * *AmazonHelp Response* (ID `644`): "@115835 I'm so sorry you didn't receive your parcel! We'd like a chance to look into this with you here: https://t.co/JzP7hlA23B ^SY"

2. **Customer** (ID `5128`): "@AmazonHelp AMZL US Tracking ID TBA566517950000 it says delivered to mail room, I checked the mail and the front offce, the driver listed 1 package, in that one package was my XLR cables...I'm missing the controller."
   * *AmazonHelp Response* (ID `5126`): "@116914 I understand your frustration! Our team would like a chance to address this concern. At your convenience, include your details here: https://t.co/hKZOmv3DMU ^SJ"

3. **Customer** (ID `45558`): "So I still don't have my @115830 order I was supposed to get on Monday. No explanation as to why. Probably been stolen!"
   * *AmazonHelp Response* (ID `45557`): "@118232 Sorry you don't have your order! We'd like to see how we can help so please reach us by phone here: https://t.co/JzP7hlA23B ^DD"

4. **Customer** (ID `49922`): "Ok @115850 let's get it sorted today. I've bought over a 100 books from u, never received a single free bookmark. 😢
Mujhe Insaf chaiye! 😢"
   * *AmazonHelp Response* (ID `49920`): "@127182 to provide a better shopping experience. (3/3) ^JS"

---

### `account_access_and_security` — Account Access & Security

* **Empirical Volume**: 322 records (1.61%)
* **Definition**: Customer cannot log in, password reset fails, two-factor OTP is not received, account is on hold/suspended by Account Specialists, or customer suspects fraud.
* **Boundary**: Covers authentication, credentials, and account status. Does not cover recurring subscription management (which belongs to 'prime_and_subscriptions').
* **Confusing Intents**: payment_and_billing_issues, prime_and_subscriptions
* **Typical Resolution**: AmazonHelp firmly states that personal account actions cannot be executed on public Twitter; directs customer to reply directly to Account Specialist email or access official secure identity verification flows.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `2581`): "@AmazonHelp I've been in the prime queue, kindle queue, the echo queue, and now on hold again."
   * *AmazonHelp Response* (ID `2582`): "@116322 We'd like to look deeper into this issue. Please provide us with more information here: https://t.co/wpDDiHUP4k. ^LH"

2. **Customer** (ID `4850`): "@AmazonHelp already tried help by mail and still problem persist, please close my account and don't want to be a customer anymore https://t.co/m2g5tP26fX"
   * *AmazonHelp Response* (ID `4846`): "@116849 I'm sorry. We can't access your account via Twitter. For assistance, please reach us here: https://t.co/jzvkhdlrK5 ^WT"

3. **Customer** (ID `9129`): "@AmazonHelp It looks as though someone has changed the email address linked to my acct &amp; I can no longer log in. Help!"
   * *AmazonHelp Response* (ID `9128`): "@117632 We're here to help! Please, reach us phone or e-mail so we can investigate: https://t.co/jzvkhdlrK5 ^EB"

4. **Customer** (ID `10645`): "@AmazonHelp did amazon get hacked?"
   * *AmazonHelp Response* (ID `10644`): "@117949 We'd like to help! Have you noticed any unauthorized activity on your account? ^VB"

---

### `payment_and_billing_issues` — Payment & Billing Issues

* **Empirical Volume**: 102 records (0.51%)
* **Definition**: Customer reports unknown or unauthorized charges, double billing, card declined, currency conversion discrepancies, or gift card/promo balance failures.
* **Boundary**: Covers transactional payment discrepancies and unauthorized debits. Prime renewal billing questions belong to 'prime_and_subscriptions'.
* **Confusing Intents**: refund_inquiry, prime_and_subscriptions, account_access_and_security
* **Typical Resolution**: AmazonHelp clarifies potential temporary bank authorization holds and directs the customer to phone/chat support to verify billing details securely without exposing cards.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `1710`): "@AmazonHelp where can I chat with a support member for a false charge"
   * *AmazonHelp Response* (ID `1709`): "@116084 I'm sorry you've encountered an unknown charge! We'd be happy to look into this with you here: https://t.co/hApLpMlfHN ^BL"

2. **Customer** (ID `21447`): "@115850 i want to cancel my order but there is no option of cancellation Help I have made e-payment by debit card"
   * *AmazonHelp Response* (ID `2663414`): "@750569 here: https://t.co/vlvfJr4nN9 and we'll check it for you. 2/2 ^SY"

3. **Customer** (ID `91325`): "@AmazonHelp 10% cashback on debit card payment while COD , i did two times got nothing yet"
   * *AmazonHelp Response* (ID `91327`): "@135808 Apologies for the trouble with your cashback. Have you reported this to our support team here: https://t.co/vlvfJr4nN9? ^RB"

4. **Customer** (ID `108201`): "Amazon- worst experience. Ordered phone got different one. Left with credit card bill and a phone- notmy choice. @115850 @115821 helpless"
   * *AmazonHelp Response* (ID `108199`): "@140017 Sorry to know you've received a different product, Falguni. Please reach us from here: https://t.co/rS49hgaADF we'll check your details and assist you further. ^SV"

---

### `damaged_defective_or_wrong_item` — Damaged, Defective, or Wrong Item

* **Empirical Volume**: 541 records (2.71%)
* **Definition**: Customer received a product that arrived physically broken, shattered, crushed, malfunctioning/defective, expired, counterfeit, or is a completely incorrect item.
* **Boundary**: Covers the physical state of the goods upon unboxing. General return requests for unwanted/unopened items belong to 'return_and_replacement'.
* **Confusing Intents**: return_and_replacement, service_complaints_and_feedback
* **Typical Resolution**: AmazonHelp apologizes for damaged/incorrect merchandise and directs customer to the Online Returns Center to request an immediate free replacement or return label.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `1735`): "@AmazonHelp Fulfilled by Amazon. It’s quite disturbing you’re selling counterfeit items, and can’t be trusted."
   * *AmazonHelp Response* (ID `1737`): "@116091 We'd like to look into this with you in real time, Bry. When you can, please ring or chat in with us: https://t.co/JzP7hlA23B ^BL"

2. **Customer** (ID `9781`): "I seem to have bad luck in trying to get undamaged books from @115821. Sometimes it's damaged in delivery, but this one was packed this way. https://t.co/HnwtSE7e31"
   * *AmazonHelp Response* (ID `9779`): "@117790 I'm sorry about the damage, Raymond! Have you explored options for refund/replacement here: https://t.co/Y5jpI9gRhE? ^SH"

3. **Customer** (ID `9784`): "@115821 , #fake I phone 7 received from amazon , India - order ID: amazon India has refused to replace @115850 pictures attach herewith. https://t.co/iYmtFWzE6o"
   * *AmazonHelp Response* (ID `9783`): "@117791 Please don't provide your details, we consider it personal information. Our Twitter page is visible to public. 2/2 ^MK"

4. **Customer** (ID `13189`): "Hi @AmazonHelp, I’ve purchased something via your app and it’s broken! How can I get it replaced?"
   * *AmazonHelp Response* (ID `13187`): "@118710 Hi, Reece! I'm sorry about the broken item. You can check into options here: https://t.co/Ueduyt85xq ^BL"

---

### `refund_inquiry` — Refund Inquiry & Status

* **Empirical Volume**: 802 records (4.01%)
* **Definition**: Customer inquires about the status, timeline, or amount of a refund for a returned or canceled item, or complains that promised funds have not posted to their bank.
* **Boundary**: Focuses specifically on monetary reimbursement. Questions about return shipping labels or drop-off logistics belong to 'return_and_replacement'.
* **Confusing Intents**: return_and_replacement, payment_and_billing_issues
* **Typical Resolution**: AmazonHelp outlines standard banking turnaround times (3-5 business days for cards, 24 hours for Amazon Gift Card balance) and directs customer to 'Your Orders' -> 'View Return/Refund Status'.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `14855`): "@115821 407-8406190-7752345. i want refund amount -1399/- amazon seller was lying. amazon custamare care side also."
   * *AmazonHelp Response* (ID `14852`): "@119214 Please don't provide your order details, we consider it to be personal information. Our page is visible to the public. ^SC"

2. **Customer** (ID `16757`): "@AmazonHelp No one knows what to do to get my refund back to me! https://t.co/q71Ycboikm"
   * *AmazonHelp Response* (ID `16759`): "@119697 I'm sorry for the trouble. Generally, the bank can issue a refund to the new active card on file. Please keep us updated. ^LR"

3. **Customer** (ID `16805`): "@AmazonHelp Amazon its a complete fraud now u are saying u will ship till 7th please for god sake #help #cancelorder #refund #fraud #poorcustomerservice https://t.co/riuEM7g6om"
   * *AmazonHelp Response* (ID `16806`): "@119701 Could you please let us know if you had received any email stating the package was  going to be shipped by 7th ? ^KS"

4. **Customer** (ID `16817`): "@AmazonHelp When will i be getting a refund of this product #help #pleasebesensable https://t.co/gGgeU6tmhP"
   * *AmazonHelp Response* (ID `16818`): "@119701 Our team has sent you a correspondence. Kindly check it here: https://t.co/8DAc10S7ww ^AP"

---

### `order_cancellation_and_modification` — Order Cancellation & Modification

* **Empirical Volume**: 101 records (0.51%)
* **Definition**: Customer requests to cancel an order, modify quantities, correct a shipping address, or fix an accidental duplicate order before shipment.
* **Boundary**: Applies to pre-fulfillment adjustments. Post-delivery return requests belong to 'return_and_replacement'.
* **Confusing Intents**: return_and_replacement, delivery_status_and_delay
* **Typical Resolution**: AmazonHelp explains that orders can be canceled self-service only while in 'Order Placed' status before dispatch; advises refusing the package or initiating a return if already shipped.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `114312`): "Why does amazon take my money but then cancel my order? @AmazonHelp"
   * *AmazonHelp Response* (ID `114310`): "@141410 I'm sorry for the order issues! We won't charge you for an order until it ships! What you're likely seeing is an authorisation charge, which should fall off shortly. More information about authorisation charges can be found here: https://t.co/KEzhggtDZC ^WT"

2. **Customer** (ID `132579`): "@115850 need help with my recent order. Order id is 406-7212644-2072325. I need to change my shipping address. Need help. Thanks."
   * *AmazonHelp Response* (ID `132577`): "@145911 Also, please don't provide your order details, as we consider it to be personal information. Our Twitter page is visible to the public. ^AP"

3. **Customer** (ID `182923`): "@AmazonHelp Any updates after 21hours? I want to cancel order. Let me know how to proceed. No cancellation action on the website"
   * *AmazonHelp Response* (ID `182924`): "@158356 We've sent you a correspondence. Kindly check the same here: https://t.co/ubzNHWZvL2 ^SG"

4. **Customer** (ID `229799`): "@AmazonHelp Yes @127161 have managed to deliver to the wrong address and even got a signature - useless"
   * *AmazonHelp Response* (ID `229802`): "@170764 Sorry to hear that, have you been able to locate the parcel: https://t.co/L76CBge35P? ^JJ"

---

### `return_and_replacement` — Return & Replacement Logistics

* **Empirical Volume**: 584 records (2.92%)
* **Definition**: Customer asks about return policies, return windows, prepaid return labels, drop-off locations (UPS, Kohl's), or status of an ongoing item exchange/replacement.
* **Boundary**: Covers return logistics and procedural questions. Defective/damaged complaints belong to 'damaged_defective_or_wrong_item'; monetary refund queries belong to 'refund_inquiry'.
* **Confusing Intents**: damaged_defective_or_wrong_item, refund_inquiry
* **Typical Resolution**: AmazonHelp provides instructions on generating return labels via the Online Returns Center and details label-free, box-free drop-off options.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `5219`): "@115850 I hope there will be a good exchange offer for Oneplus 5 users"
   * *AmazonHelp Response* (ID `702959`): "@287911 Considering that One plus 5T in on flash sale, we do not have any information regarding the availability of exchange option. ^KA"

2. **Customer** (ID `9780`): "@AmazonHelp I've returned several things lately and don't want Amazon to think I'm abusing the return policy."
   * *AmazonHelp Response* (ID `9782`): "@117790 I understand! Returns can be made as long as they fall under this policy: https://t.co/i3QyGkjfQI. Hope this helps! ^BL"

3. **Customer** (ID `15686`): "@AmazonHelp Order no - 403-7559101-5645129 
Return reference - 710398288491
Article name - puma shoes"
   * *AmazonHelp Response* (ID `15684`): "@119451 number. Also, please don't provide order details, we consider it to be personal info. Our page is visible to the public.(2/2)^SF"

4. **Customer** (ID `19118`): "@AmazonHelp can u ready for return pick up i receive damage product"
   * *AmazonHelp Response* (ID `19116`): "@120261 You must have received a correspondence from our team, request you to check the same. ^SH"

---

### `prime_and_subscriptions` — Prime & Subscription Management

* **Empirical Volume**: 332 records (1.66%)
* **Definition**: Customer asks about Prime membership benefits, subscription fees, trial cancellation, student discounts, or services such as Music Unlimited, Kindle Unlimited, and Audible.
* **Boundary**: Relates to ongoing subscription services and membership perks. General technical app crashes belong to 'digital_services_and_device_support'.
* **Confusing Intents**: payment_and_billing_issues, digital_services_and_device_support
* **Typical Resolution**: AmazonHelp directs the customer to 'Manage Prime Membership' in Account Settings and confirms refund eligibility if membership benefits were not used.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `18392`): "@115850  what’s the use of amazon prime membership if the product reaches me after 2 days of placing the order .. al false promises"
   * *AmazonHelp Response* (ID `18391`): "@120086 Prime subscribers are eligible to get free One-day or Two-day shipping. May I please know if the package was 1/2 ^SH"

2. **Customer** (ID `19141`): "@115850 I am a prime member but i can't get product so fast.."
   * *AmazonHelp Response* (ID `735628`): "@295977 Could you help us with the product link &amp; pin-code? We'll be glad to check this for you. 2/2 ^MJ"

3. **Customer** (ID `19164`): "@115850 I m not getting the fast delivery even i m prime member but don't get 1&amp;2 days delivery ...."
   * *AmazonHelp Response* (ID `2310218`): "@670021 Guaranteed delivery is only offered to select cities and available on eligible items.  1/2 ^AH"

4. **Customer** (ID `19469`): "@AmazonHelp I was scammed. 6 orders, all sellers are gone and nothing send to me, how could I do now? how to stop my prime membership?"
   * *AmazonHelp Response* (ID `19467`): "@120322 sorry to hear that, from what Amazon marketplace were you shopping from? .com, .co.uk, .es etc? ^AS"

---

### `digital_services_and_device_support` — Digital Services & Device Support

* **Empirical Volume**: 566 records (2.83%)
* **Definition**: Technical troubleshooting for Amazon devices (Fire TV Stick, Echo, Kindle e-readers) and digital streaming services (Prime Video playback, Alexa app, digital downloads).
* **Boundary**: Focuses on technical bugs, software glitches, and device configurations. Physical shipping of devices belongs to 'delivery_status_and_delay'.
* **Confusing Intents**: prime_and_subscriptions, service_complaints_and_feedback
* **Typical Resolution**: AmazonHelp provides standard diagnostic steps (restart device, force stop app, clear cache, update firmware) and links to device-specific troubleshooting guides.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `5805`): "@117095 @115821 My audiobook hasn’t shipped (but the site still says I’ll get it by 8PM 🙄)"
   * *AmazonHelp Response* (ID `5804`): "@117094 I'm sorry for the wait! Please let us know if it does not arrive by 8PM. We want to make sure you receive the order. ^DD"

2. **Customer** (ID `8524`): "@AmazonHelp my original echo some time say things without asking here anything ! This is really wired and creepy and scary!!"
   * *AmazonHelp Response* (ID `8523`): "@117497 Hmm, that's strange! Try going to Settings and reviewing your history. From here, you can see what prompted your Echo. ^FD"

3. **Customer** (ID `17254`): ".@115850 will Echo help in playing Antakshari or if we could play same with her? :P #pp"
   * *AmazonHelp Response* (ID `17253`): "@119797 You can ask Alexa, and it would play the song for you :) ^KA"

4. **Customer** (ID `18708`): "@AmazonHelp Also when will Amazon prime music be available for Indian users of Alexa?"
   * *AmazonHelp Response* (ID `18710`): "@120174 In order to stream music from Amazon Prime Music on the echo devices, the customer has to be an Amazon Prime member. 2/2^AR"

---

### `service_complaints_and_feedback` — Service Complaints & Feedback

* **Empirical Volume**: 9,768 records (48.84%)
* **Definition**: Customer complains about poor customer support interactions, rude delivery drivers (e.g., throwing packages, property damage), long hold times, or deceptive seller behavior.
* **Boundary**: Involves customer grievances and operational feedback without a distinct self-service action. Specific delivery delay inquiries belong to 'delivery_status_and_delay'.
* **Confusing Intents**: missing_package_false_delivery, delivery_status_and_delay
* **Typical Resolution**: AmazonHelp offers a sincere apology, collects carrier/driver details to log internal driver coaching feedback, and escalates to senior support if requested.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `645`): "@AmazonHelp That page is useless - doesn’t allow me to state it hasn’t been delivered; only tells me it has! How can you sort this out?"
   * *AmazonHelp Response* (ID `647`): "@115835 You can also request a call back here Martin https://t.co/zH8UlhTGcc ^KM"

2. **Customer** (ID `685`): "@AmazonHelp Details sent. Please check."
   * *AmazonHelp Response* (ID `687`): "@115849 Thanks for confirming that the details have been shared. Our team will give it a look and reach out shortly. ^AB"

3. **Customer** (ID `1698`): "@AmazonHelp Thats the thing I told customer service. I created a new email address for the Prime trial and forgot it. What can I do so I'm not charged?"
   * *AmazonHelp Response* (ID `1700`): "@116082 Hey Corey! Even on the new account you made you can turn of the auto renew through the same link ^SK posted for you. ^AJ"

4. **Customer** (ID `1752`): "@116096 Truly. This is the strangest vampire book I’ve ever received. 😜 cc @43760 @AmazonHelp #misship https://t.co/Zad7Az14Zg"
   * *AmazonHelp Response* (ID `1750`): "@116095 I'm sorry you received an incorrect item. Have you checked out our return/replacement options here: https://t.co/FRsodhtXKJ? ^FJ"

---

### `delivery_status_and_delay` — Delivery Status & Delay

* **Empirical Volume**: 6,495 records (32.48%)
* **Definition**: Customer asks where their order/package is, reports that shipment is late or delayed, inquiries why an order has not shipped, or asks for updated tracking details.
* **Boundary**: The baseline delivery inquiry intent. Does NOT include packages marked 'Delivered' that were not received (which belongs to 'missing_package_false_delivery').
* **Confusing Intents**: missing_package_false_delivery, order_cancellation_and_modification
* **Typical Resolution**: AmazonHelp checks carrier status, directs customer to 'Your Orders' tracking page, explains transit window expectations, or offers shipping fee refunds if Prime date was missed.

#### Positive Examples (Real Customer Messages & Historical AmazonHelp Responses)
1. **Customer** (ID `628`): "@115828 How about you guys figure out my Xbox One X project Scorpio edition first. No expected delivery or shipping date and it’s only a week away"
   * *AmazonHelp Response* (ID `626`): "@115826 I'm sorry for the wait. You'll receive an email as soon as we have an estimated delivery date. ^FJ"

2. **Customer** (ID `672`): "I'm NEVER using Amazon again! After waiting in all day as item is "out for delivery", they've only gone and sent it to the WRONG COUNTRY!"
   * *AmazonHelp Response* (ID `674`): "@115844 Oh no! We're here to help! Without providing account details will you give us more information about what has happened? ^SE"

3. **Customer** (ID `678`): "My package from @115821 with my Halloween costume was “delivered” Friday but I don’t have I so searching everywhere for a last minute idea."
   * *AmazonHelp Response* (ID `679`): "@115846 Sorry about your costume, Mike! Who's the carrier responsible for the delivery? Let's check here: https://t.co/Y5jpI9gRhE ^JZ"

4. **Customer** (ID `2568`): "Hey @115821, why is your Prime 2-day delivery not arriving until Monday? Is there a holiday I don't know about?"
   * *AmazonHelp Response* (ID `2566`): "@116320 Most items are readily available for shipping; however, some aren't and may have a longer processing time than others. ^QJ"

---

## 3. Final Recommendation & Design Rationale

### Proposed Final Intents (11 Intents)
1. `delivery_status_and_delay`
2. `missing_package_false_delivery`
3. `damaged_defective_or_wrong_item`
4. `return_and_replacement`
5. `refund_inquiry`
6. `order_cancellation_and_modification`
7. `payment_and_billing_issues`
8. `prime_and_subscriptions`
9. `account_access_and_security`
10. `digital_services_and_device_support`
11. `service_complaints_and_feedback`

### Why 11 Intents?
* **High Semantic Separation**: 11 categories perfectly balances granularity against annotation ambiguity. An e-commerce domain cannot be collapsed into 3–4 categories without losing critical business logic (e.g., bundling missing parcels with damaged items obscures fraud risks). Conversely, splitting into 30+ micro-intents creates severe label confusion and sparse evaluation classes.
* **Escalation Alignment**: The taxonomy explicitly isolates high-risk escalation drivers (`account_access_and_security`, `payment_and_billing_issues`, `missing_package_false_delivery`) from low-risk automated triage candidates (`delivery_status_and_delay`, `return_and_replacement`).

### Categories Merged
1. **Pre-order Tracking & Delivery Delays**: Initially considered separating *"Where is my package?"* from *"My package is delayed."* In practice, both follow identical conversational trajectories (checking tracking status in Order History), so they were merged into `delivery_status_and_delay`.
2. **Returns and Replacements**: Queries regarding replacement units for undamaged items and return labels were unified into `return_and_replacement`.
3. **Hardware Devices & Digital Video/Audio**: Kindle, Fire TV, Echo, and Prime Video issues were unified under `digital_services_and_device_support` because AmazonHelp applies standard multi-device diagnostic flows (reboot, clear cache, deregister) across all of them.

### Categories Split
1. **`delivery_status_and_delay` vs. `missing_package_false_delivery`**:
   * *Rationale*: Tracking delays indicate logistical bottlenecks, whereas a status claiming "Delivered" when the package is missing signals potential theft, porch piracy, or premature carrier scans. The resolution paths differ drastically (patience/re-tracking vs. police report/stolen parcel investigation).

### Categories Rejected
1. **Banking77 Taxonomy**: Rejected completely. Banking77 includes irrelevancies such as ATM fees, wire transfers, and exchange rates that do not reflect Amazon retail support.
2. **Product Price Inquiries / Availability**: Almost non-existent in inbound support; customer mentions were almost universally related to placed orders rather than pre-sales inquiries.

### Important Ambiguities & Edge Cases
* **Multi-issue Inquiries**: E.g., *"My order arrived 4 days late AND the teapot is broken."* Annotation guideline: prioritize the physical resolution requirement (`damaged_defective_or_wrong_item`) over the delivery delay.
* **Aggressive Tone / Sarcasm**: E.g., *"Thanks Amazon for ruining my daughter's birthday with no gift."* If no other problem is stated, classified as `service_complaints_and_feedback`; if tracking or delay is mentioned, classified as `delivery_status_and_delay`.

### Limitations of Discovery Method
* Discovery relies on keyword clustering and heuristic parsing over single customer messages. In subsequent phases, full multi-turn context and manual golden set review will refine edge-case boundaries.
