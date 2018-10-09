
/*
select
a.*, b.*
from
dw.dw_user_coupon a
join
dw.dw_order_fact b on a.user_id=b.user_id and substr(a.use_time, 1, 10)= substr(b.result_pay_time, 1, 10)
where a.status=1
limit 100
*/

---b.order_total_amount - b.shipping_money - b.tax - b.goods_amount

create table zybiro.bi_gu_orders_with_coupon as
select
a.*, b.*
from
dw.dw_order_fact b
left join
dw.dw_user_coupon a on a.user_id=b.user_id and substr(a.use_time, 1, 10)= substr(b.result_pay_time, 1, 10)
and ((a.promote_strategy = 1 and (a.rule_value + (100 * ((b.order_total_amount - b.shipping_money - b.tax - b.goods_amount) / b.goods_amount))) <= 5
and (a.rule_value + (100 * ((b.order_total_amount - b.shipping_money - b.tax - b.goods_amount) / b.goods_amount))) >= 0) or (a.promote_strategy = 2 and
(a.rule_value + (b.order_total_amount - b.shipping_money - b.tax - b.goods_amount)) <= 5 and (a.rule_value + (b.order_total_amount - b.shipping_money - b.tax - b.goods_amount)) >= 0))


select a.*, b.*
from
dw.dw_user_coupon a
join
dw.dw_order_fact b on a.user_id=b.user_id and substr(a.use_time, 1, 10) = substr(b.result_pay_time, 1, 10) and
(select
where a.status = 1 and ((a.promote_strategy = 1
and (a.rule_value + (100 * ((b.order_total_amount - b.shipping_money - b.tax - b.goods_amount) / b.goods_amount))) <= 5
and (a.rule_value + (100 * ((b.order_total_amount - b.shipping_money - b.tax - b.goods_amount) / b.goods_amount))) >= 0) or
(a.promote_strategy = 2
and (a.rule_value + (b.order_total_amount - b.shipping_money - b.tax - b.goods_amount)) <= 5
and (a.rule_value + (b.order_total_amount - b.shipping_money - b.tax - b.goods_amount)) >= 0))

create zybiro.bi_gu_filtered_consume as
select user_id, app_name, total_paid_orders, total_paid_order_amount, total_paid_discount_amount, total_paid_goods_num, total_canceled_orders, total_canceled_order_amount, total_order_1st_cats, last_1y_paid_orders, last_1y_paid_order_amount, last_1y_paid_discount_amount, last_1y_paid_goods_num,  last_90d_paid_orders, last_90d_paid_order_amount, last_90d_paid_discount_amount, last_90d_paid_goods_num
from dw.dw_user_consume_info where data_date = '20180901'

create table zybiro.bi_gu_user_info as
select b.*, a.reg_time, a.reg_days, a.cookie_id, a.device_id, a.site_id, a.os, a.medium, a.source,
a.campaign, a.district, a.country, a.city, a.reg_method, a.pagename, a.nick_name, a.sex, a.sex_af, a.age, a.age_group, a.career, a.risk_type,
a.end_order_type, a.end_num, a.end_rec_num, a.account_balance, a.coupon_amt, a.coupon_num, a.coins, a.extreme_start_time, a.extreme_expire_time,
a.is_extreme, a.extreme_card_sn, a.cod_risk_grade
from
zybiro.bi_gu_filtered_consume b
join
dw.dw_user_base_info a on a.user_id=b.user_id and a.app_name=b.app_name

create table zybiro.bi_gu_user_info as
select b.*, a.reg_time, a.reg_days, a.cookie_id, a.device_id, a.site_id, a.os, a.medium, a.source,
a.campaign, a.district, a.country, a.city, a.reg_method, a.pagename, a.nick_name, a.sex, a.sex_af, a.age, a.age_group, a.career, a.risk_type,
a.end_order_type, a.end_num, a.end_rec_num, a.account_balance, a.coupon_amt, a.coupon_num, a.coins, a.extreme_start_time, a.extreme_expire_time,
a.is_extreme, a.extreme_card_sn, a.cod_risk_grade
from
zybiro.bi_gu_filtered_consume b
join
dw.dw_user_base_info a on a.user_id=b.user_id and a.app_name=b.app_name
where a.data_date = '20180901'

create table zybiro.bi_gu_discount_tag as
select
 floor((total_paid_discount_amount / (total_paid_order_amount + total_paid_discount_amount))/.05)*.05 as bucket_floor,
 count(*) as count, sum(total_paid_order_amount) / count(*) as avg_paid_order_amount, sum(total_paid_discount_amount) / count(*) as avg_paid_discount_amount,
 ((sum(total_paid_order_amount) / count(*)) + (sum(total_paid_discount_amount) / count(*))) as total_org_amount
from zybiro.bi_gu_user_info
where app_name = 'JC'  and total_paid_order_amount >= 0 and total_paid_discount_amount >= 0
group by 1
order by 1;

create table zybiro.bi_gu_goods_info as
select distinct goods_id, category_name, sub_category_name, shop_price, goods_sn, cat_id, cat_level3_name from dw.dw_goods_on_sale where data_date = '20180901'

create table zybiro.bi_gu_goods_cat_info as
select a.*, b.category_name, b.sub_category_name, b.cat_id, b.cat_level3_name, b.shop_price from dw.dw_order_goods_fact a left join zybiro.bi_gu_goods_info b on a.goods_id = b.goods_id

create table zybiro.bi_gu_user_cookie_goods as
select b.user_id, c.cookie_id, c.site_id, c.device_id,
a.goods_id, a.goods_name, a.cat_id, a.category_name
from zybiro.bi_gu_goods_cat_info a
join dw.dw_order_fact b
on a.order_id = b.order_id
join zybiro.bi_gu_user_info c
on c.user_id = b.user_id

create table zybiro.bi_gu_user_top10_goods as
(select user_id, cookie_id, site_id, device_id,
max(1goods) as good_id_1, max(2goods) as good_id_2, max(3goods) as good_id_3,
max(4goods) as good_id_4, max(5goods) as good_id_5, max(6goods) as good_id_6,
max(7goods) as good_id_7, max(8goods) as good_id_8, max(9goods) as good_id_9,
max(10goods) as good_id_10
from
(select user_id, cookie_id, site_id, device_id, goods_name,
case when seqnum = 1 then goods_id end as 1goods,
case when seqnum = 2 then goods_id end as 2goods,
case when seqnum = 3 then goods_id end as 3goods,
case when seqnum = 4 then goods_id end as 4goods,
case when seqnum = 5 then goods_id end as 5goods,
case when seqnum = 6 then goods_id end as 6goods,
case when seqnum = 7 then goods_id end as 7goods,
case when seqnum = 8 then goods_id end as 8goods,
case when seqnum = 9 then goods_id end as 9goods,
case when seqnum = 10 then goods_id end as 10goods
from
(select user_id, cookie_id, site_id, device_id, goods_name, goods_id, goods_freq,
row_number() over (partition by user_id order by goods_freq desc) as seqnum from
(select user_id, cookie_id, site_id, device_id, goods_name, goods_id, count(goods_id) as goods_freq
from zybiro.bi_gu_user_cookie_goods
group by user_id, cookie_id, site_id, device_id, goods_name, goods_id) a) b
where seqnum between 1 and 10) c
group by user_id, cookie_id, site_id, device_id)

create table zybiro.bi_gu_user_top3_cat as
(select user_id, cookie_id, site_id, device_id,
max(1goods) as cat_id_1, max(2goods) as cat_id_2, max(3goods) as cat_id_3
from
(select user_id, cookie_id, site_id, device_id, category_name,
case when seqnum = 1 then cat_id end as 1goods,
case when seqnum = 2 then cat_id end as 2goods,
case when seqnum = 3 then cat_id end as 3goods
from
(select user_id, cookie_id, site_id, device_id, category_name, cat_id, cat_freq,
row_number() over (partition by user_id order by cat_freq desc) as seqnum from
(select user_id, cookie_id, site_id, device_id, category_name, cat_id, count(cat_id) as cat_freq
from zybiro.bi_gu_user_cookie_goods
group by user_id, cookie_id, site_id, device_id, category_name, cat_id) a) b
where seqnum between 1 and 3) c
group by user_id, cookie_id, site_id, device_id)

create table zybiro.bi_gu_user_top_goods_cat as
select a.*, b.cat_id_1, b.cat_id_2, b.cat_id_3
from zybiro.bi_gu_user_top10_goods a
join zybiro.bi_gu_user_top3_cat b
on a.user_id = b.user_id


create table zybiro.bi_gu_user_cat_vec as
select user_id, cookie_id, site_id, device_id, 10000000*wc/56867475 as WomensClothing, 10000000*wa/19135465 as WomensAccesories,
10000000*be/19130684 as Beauty, 10000000*k/11657964 as Kids, 10000000*wb/11372703 as WomensBags,
10000000*ws/10794722 as WomensShoes, 10000000*cpd/9974967 as CellPhonesDigital,
10000000*mc/11138937 as MensClothing, 10000000*d/6539236 as Decor, 10000000*o/26179238 as Other
from
(select user_id, cookie_id, site_id, device_id, max(WomensClothing)as wc, max(WomensAccesories) as wa,
max(Beauty) as be, max(Kids) as k, max(WomensBags) as wb, max(WomensShoes) as ws, max(CellPhonesDigital) as cpd,
max(MensClothing) as mc, max(Decor) as d, max(Other) as o from
(select user_id, cookie_id, site_id, device_id,
case when category_name = "Women\'s Clothing" then cat_freq end as WomensClothing,
case when category_name = "Women\'s Accessories" then cat_freq end as WomensAccesories,
case when category_name = "Beauty" then cat_freq end as Beauty,
case when category_name = "Kids" then cat_freq end as Kids,
case when category_name = "Women\'s Bags" then cat_freq end as WomensBags,
case when category_name = "Women\'s Shoes" then cat_freq end as WomensShoes,
case when category_name = "Cell Phones & Digital" then cat_freq end as CellPhonesDigital,
case when category_name = "Men\'s Clothing" then cat_freq end as MensClothing,
case when category_name = "Décor" then cat_freq end as Decor,
case when category_name not in ("Women\'s Clothing", "Women\'s Accessories", "Beauty", "Kids", "Women\'s Bags", "Women\'s Shoes", "Cell Phones & Digital", "Men\'s Clothing")
then cat_freq end as Other
from
(select user_id, cookie_id, site_id, device_id, category_name, count(category_name) as cat_freq from zybiro.bi_gu_user_cookie_goods
group by user_id, cookie_id, site_id, device_id, category_name) a) b
group by user_id, cookie_id, site_id, device_id) c
