from datetime import datetime

class BaseModel:
    def __init__(self) -> None:
        pass

    def registerAlert(self, alertdic, alert_name: str, alert_date: datetime):
        if alert_name in self.Alertdic:
            alertdic[alert_name].append(alert_date)
        else:
            alertdic.setdefault(alert_name, [alert_date])

class DR_300(BaseModel):
    #クラス変数
    Name = "DR-300"
    def __init__(self) -> None:
        super().__init__()
        self.Alertdic = {}
    def registerAlert(self, alert_name: str, alert_date: datetime):
        super().registerAlert(self.Alertdic, alert_name, alert_date)

class BresTome(BaseModel):
	#クラス変数
	Name = "BresTome"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class CVS_MPC(BaseModel):
	#クラス変数
	Name = "CVS_MPC"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class CVS_MPC_2(BaseModel):
	#クラス変数
	Name = "CVS_MPC_2"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class DAR_3500(BaseModel):
	#クラス変数
	Name = "DAR-3500"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class DAR_7500(BaseModel):
	#クラス変数
	Name = "DAR-7500"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class DAR_8000(BaseModel):
	#クラス変数
	Name = "DAR-8000"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class DR_200(BaseModel):
	#クラス変数
	Name = "DR-200"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class Elmammo(BaseModel):
	#クラス変数
	Name = "Elmammo"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class FlexaF3(BaseModel):
	#クラス変数
	Name = "FlexaF3"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class FlexaF4(BaseModel):
	#クラス変数
	Name = "FlexaF4"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class FLUOROspeed_X1(BaseModel):
	#クラス変数
	Name = "FLUOROspeed.X1"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class PET_MPC(BaseModel):
	#クラス変数
	Name = "PET_MPC"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class RADspeedProEDGE(BaseModel):
	#クラス変数
	Name = "RADspeedProEDGE"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class Trinias(BaseModel):
	#クラス変数
	Name = "Trinias"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class Trinias_Opera(BaseModel):
	#クラス変数
	Name = "Trinias.Opera"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)

class Trinias_smart(BaseModel):		
	#クラス変数
	Name = "Trinias.smart"
	def __init__(self) -> None:
		super().__init__()
		self.Alertdic = {}
	def registerAlert(self, alert_name: str, alert_date: datetime):
		super().registerAlert(self.Alertdic, alert_name, alert_date)
