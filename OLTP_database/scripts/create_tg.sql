CREATE OR REPLACE FUNCTION updated_at_tg()
RETURNS TRIGGER AS
$$
BEGIN
	NEW.updated_at := NOW();
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_catogories_updated_at 
BEFORE UPDATE ON categories 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();

CREATE TRIGGER trg_competitor_updated_at 
BEFORE UPDATE ON competitor 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_currency_updated_at 
BEFORE UPDATE ON currency 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_empl_updated_at 
BEFORE UPDATE ON employees
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_product_updated_at 
BEFORE UPDATE ON product 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_purch_updated_at 
BEFORE UPDATE ON purchase_status
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_sale_statust_updated_at 
BEFORE UPDATE ON sale_status 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_stock_updated_at 
BEFORE UPDATE ON stock 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_st_hist_updated_at 
BEFORE UPDATE ON stock_history
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_store_updated_at 
BEFORE UPDATE ON store 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();



CREATE TRIGGER trg_supplier_updated_at 
BEFORE UPDATE ON supplier 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_tax_rate_updated_at 
BEFORE UPDATE ON tax_rate 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


CREATE TRIGGER trg_uomt_updated_at 
BEFORE UPDATE ON uom 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();



CREATE TRIGGER trg_warehouse_updated_at 
BEFORE UPDATE ON warehouse 
FOR EACH ROW 
EXECUTE FUNCTION updated_at_tg();


