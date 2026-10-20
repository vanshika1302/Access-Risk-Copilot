-- Controls. Labels (denied) are used ONLY from split = 'train' so evaluation splits stay clean.

-- C1 Segregation of Duties: one manager's APPROVED requests for the same resource come from both
-- roles (ROLE_FAMILY) of a conflicting pair. sod_pairs is created by etl/load.py.
create or replace view ctrl_sod as
select r.request_id, 'SOD' as control,
       p.fam_a || ' vs ' || p.fam_b as detail
from requests r
join sod_pairs p on r.role_family in (p.fam_a, p.fam_b)
where exists (
  select 1 from requests o
  where o.mgr_id = r.mgr_id and o.resource = r.resource and o.request_id <> r.request_id
    and o.target = 1 and r.target = 1
    and o.role_family = case when r.role_family = p.fam_a then p.fam_b else p.fam_a end);

-- C2 Unusual access for a department: the (department, resource) pair is under 1% of that
-- department's requests and seen fewer than 3 times in total.
create or replace view ctrl_unusual as
with pair as (select role_deptname, resource, count(*) n from requests group by 1, 2),
     dept as (select role_deptname, count(*) n from requests group by 1)
select r.request_id, 'UNUSUAL' as control,
       'dept ' || r.role_deptname || ' used resource ' || r.resource || ' in ' || p.n || ' of ' || d.n || ' requests' as detail
from requests r join pair p using (role_deptname, resource) join dept d using (role_deptname)
where p.n < 3 and p.n * 1.0 / d.n < 0.01;

-- C3 High-risk resource: top decile of resources by denial rate (train labels, >= 20 train requests).
create or replace table high_risk_resources as
with s as (select resource, count(*) n, avg(denied) rate from requests where split = 'train' group by 1 having count(*) >= 20)
select resource, n, rate from s where rate >= (select quantile_cont(rate, 0.9) from s);

create or replace view ctrl_high_risk as
select r.request_id, 'HIGH_RISK_RESOURCE' as control,
       'resource ' || r.resource || ' train denial rate ' || round(h.rate, 3) as detail
from requests r join high_risk_resources h using (resource);

create or replace view flags as
select * from ctrl_sod union all select * from ctrl_unusual union all select * from ctrl_high_risk;
