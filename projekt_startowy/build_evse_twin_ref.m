function build_evse_twin_ref()
% BUILD_EVSE_TWIN_REF  Pelny blizniak przez REFERENCJE gotowych obwodow.
% ------------------------------------------------------------------------
% Reuzywa juz zamodelowane, dzialajace obwody (Model reference):
%   - cp_circuit_io  : Inport StateC, Outport cp_voltage
%   - evse_power_io  : Inport contactor_cmd, Outport kWh
% Karty Stateflow budujemy swiezo (niezawodne):
%   - Emulator_auta : Out StateC ; In cmd,fault_inject,I_offer
%   - Wzorzec_EVSE  : In cp_voltage,auth_ok,fault_p1,I_avail ; Out duty,contactor_cmd,I_offer,pwm_on
% Sprzezenia (sygnaly double, pewne okablowanie):
%   Emulator.StateC -> CP.StateC ; CP.cp_voltage -> Wzorzec ;
%   Wzorzec.contactor_cmd*(1-fault_p1) -> PWR.contactor_cmd ; Wzorzec.I_offer -> Emulator
%
% WYMAGA wczesniej: zapisanych cp_circuit_io.slx i evse_power_io.slx z portami (patrz instrukcja).
% Model-reference przez skrypt bywa kapryśny -> jak [!], wklej komunikat, poprawie.
% ------------------------------------------------------------------------
mdl='evse_twin_ref';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);
try set_param(mdl,'BooleanDataType','off'); catch, end
try set_param(mdl,'StopTime','5'); catch, end

buildEmu(mdl); buildGolden(mdl);

% --- referencje gotowych obwodow ---
addRef(mdl,'CP','cp_circuit_io',[420 60 560 140]);
addRef(mdl,'PWR','evse_power_io',[840 400 980 470]);

% --- zrodla / nastawy ---
bA(mdl,'cmd','simulink/Sources/Step',[40 60 90 95]);
setp2(mdl,'cmd','Time','2'); setp2(mdl,'cmd','Before','1'); setp2(mdl,'cmd','After','2');
bA(mdl,'finj','simulink/Sources/Constant',[40 120 90 150]); setp2(mdl,'finj','Value','0');
bA(mdl,'auth','simulink/Sources/Constant',[40 300 90 330]); setp2(mdl,'auth','Value','1');
bA(mdl,'Iav','simulink/Sources/Constant',[40 350 90 380]);  setp2(mdl,'Iav','Value','16');
bA(mdl,'fp1','simulink/Sources/Constant',[40 430 90 460]);  setp2(mdl,'fp1','Value','0');
bA(mdl,'Imem','simulink/Discrete/Memory',[300 200 345 230]);
% brama: close = contactor_cmd * (1 - fault_p1)
bA(mdl,'one','simulink/Sources/Constant',[600 470 640 500]); setp2(mdl,'one','Value','1');
bA(mdl,'subF','simulink/Math Operations/Subtract',[680 440 715 475]);
bA(mdl,'pClose','simulink/Math Operations/Product',[760 420 795 460]);
bA(mdl,'scCP','simulink/Sinks/Scope',[620 60 660 100]);
bA(mdl,'Disp','simulink/Sinks/Display',[1040 415 1100 445]);

% --- okablowanie (sygnaly) ---
ln(mdl,'cmd','Outport',1,'Emulator_auta','Inport',1);
ln(mdl,'finj','Outport',1,'Emulator_auta','Inport',2);
ln(mdl,'Wzorzec_EVSE','Outport',3,'Imem','Inport',1);
ln(mdl,'Imem','Outport',1,'Emulator_auta','Inport',3);
ln(mdl,'Emulator_auta','Outport',1,'CP','Inport',1);          % StateC -> CP
ln(mdl,'CP','Outport',1,'Wzorzec_EVSE','Inport',1);           % cp_voltage -> Wzorzec
ln(mdl,'CP','Outport',1,'scCP','Inport',1);
ln(mdl,'auth','Outport',1,'Wzorzec_EVSE','Inport',2);
ln(mdl,'fp1','Outport',1,'Wzorzec_EVSE','Inport',3);
ln(mdl,'Iav','Outport',1,'Wzorzec_EVSE','Inport',4);
ln(mdl,'one','Outport',1,'subF','Inport',1); ln(mdl,'fp1','Outport',1,'subF','Inport',2);
ln(mdl,'Wzorzec_EVSE','Outport',2,'pClose','Inport',1);
ln(mdl,'subF','Outport',1,'pClose','Inport',2);
ln(mdl,'pClose','Outport',1,'PWR','Inport',1);                % close -> contactor_cmd
ln(mdl,'PWR','Outport',1,'Disp','Inport',1);                  % kWh

try Simulink.BlockDiagram.arrangeSystem(mdl); catch, end
fprintf('\nModel "%s" gotowy. Wymaga cp_circuit_io.slx i evse_power_io.slx z portami.\n',mdl);
fprintf('Run: cmd prowadzi A->B->C; CP daje cp_voltage; Wzorzec zamyka stycznik; PWR liczy kWh.\n');
end

% ---- referencja modelu ----
function addRef(mdl,n,refname,pos)
  ok=false;
  try, add_block('simulink/Ports & Subsystems/Model',[mdl '/' n],'Position',pos); ok=true; catch, end
  if ~ok, try add_block('built-in/ModelReference',[mdl '/' n],'Position',pos); ok=true; catch e, fprintf('  [!] Model blok %s: %s\n',n,e.message); end, end
  try set_param([mdl '/' n],'ModelName',refname); catch
     try set_param([mdl '/' n],'ModelNameDialog',refname); catch e, fprintf('  [!] set ref %s->%s: %s\n',n,refname,e.message); end
  end
end

% ---- karty Stateflow (swieze) ----
function buildEmu(mdl)
nm='Emulator_auta'; ch=getChart(mdl,nm,[140 40 360 200]);
addData(ch,'cmd','Input'); addData(ch,'fault_inject','Input'); addData(ch,'I_offer','Input');
addData(ch,'StateC','Output'); addData(ch,'i_demand','Output');
sA=addState(ch,sprintf('A_Unplugged\nentry: StateC=0; i_demand=0;'),[ 60 60 160 70]);
sB=addState(ch,sprintf('B_Connected\nentry: StateC=0; i_demand=0;'),[260 60 160 70]);
sC=addState(ch,sprintf('C_Ready\nentry: StateC=1; i_demand=min(I_offer,32);'),[470 60 190 80]);
sF=addState(ch,sprintf('Fault\nentry: StateC=0; i_demand=0;'),[260 190 160 70]);
addDefault(ch,sA,0);
addTrans(ch,sA,sB,'[cmd==1]',3,9); addTrans(ch,sB,sC,'[cmd==2]',3,9); addTrans(ch,sC,sB,'[cmd==3]',10,2);
addTrans(ch,sB,sA,'[cmd==0]',8,4); addTrans(ch,sC,sA,'[cmd==0]',7,1);
addTrans(ch,sB,sF,'[fault_inject==1]',6,12); addTrans(ch,sC,sF,'[fault_inject==1]',7,11); addTrans(ch,sF,sA,'[fault_inject==0]',9,5);
end
function buildGolden(mdl)
nm='Wzorzec_EVSE'; ch=getChart(mdl,nm,[140 300 380 480]);
addData(ch,'cp_voltage','Input'); addData(ch,'auth_ok','Input'); addData(ch,'fault_p1','Input'); addData(ch,'I_avail','Input');
addData(ch,'duty','Output'); addData(ch,'contactor_cmd','Output'); addData(ch,'I_offer','Output'); addData(ch,'pwm_on','Output');
sOp=addState(ch,'Operating',[40 70 860 350]);
sIdle=addState(ch,sprintf('Idle\nentry: pwm_on=0; duty=0; contactor_cmd=0; I_offer=0;'),[ 80 160 200 120]);
sDet =addState(ch,sprintf('Detected\nentry: pwm_on=1; I_offer=I_avail; duty=max(10,min(85,I_offer/0.6)); contactor_cmd=0;'),[360 160 240 150]);
sChg =addState(ch,sprintf('Charging\nentry: contactor_cmd=1;\nduring: I_offer=I_avail; duty=max(10,min(85,I_offer/0.6));'),[680 160 200 130]);
addDefault(ch,sIdle,0);
addTrans(ch,sIdle,sDet,'[cp_voltage>7.5 && cp_voltage<10.5 && I_avail>0]',3,9);
addTrans(ch,sDet,sChg,'[cp_voltage>4.5 && cp_voltage<7.5 && auth_ok==1]',3,9);
addTrans(ch,sChg,sDet,'[cp_voltage>7.5 && cp_voltage<10.5]',11,1);
addTrans(ch,sDet,sIdle,'[cp_voltage>10.5]',8,4);
sTrip=addState(ch,sprintf('Tripped\nentry: contactor_cmd=0; pwm_on=0; duty=0;'),[360 500 240 100]);
addTrans(ch,sOp,sTrip,'[fault_p1==1 || cp_voltage<1.5]',6,12);
addTrans(ch,sTrip,sOp,'[fault_p1==0 && cp_voltage>1.5]',9,7);
end

% ---- helpery ----
function ch=getChart(mdl,name,pos)
  add_block('sflib/Chart',[mdl '/' name],'Position',pos);
  rt=sfroot; cs=rt.find('-isa','Stateflow.Chart'); ch=[];
  for k=1:numel(cs), if strcmp(cs(k).Name,name), ch=cs(k); end, end
end
function d=addData(ch,n,s), d=Stateflow.Data(ch); d.Name=n; d.Scope=s; end
function s=addState(ch,l,p), s=Stateflow.State(ch); s.LabelString=l; s.Position=p; end
function t=addTrans(ch,a,b,l,sc,dc)
  t=Stateflow.Transition(ch); t.Source=a; t.Destination=b; if ~isempty(l), t.LabelString=l; end
  if nargin>=5&&~isempty(sc), try t.SourceOClock=sc; catch, end, end
  if nargin>=6&&~isempty(dc), try t.DestinationOClock=dc; catch, end, end
end
function addDefault(ch,d,c)
  t=Stateflow.Transition(ch); t.Destination=d; p=d.Position;
  try t.DestinationOClock=c; catch, end
  try t.SourceEndPoint=[p(1)+p(3)/2,p(2)-32]; catch, end
  try t.MidPoint=[p(1)+p(3)/2,p(2)-16]; catch, end
end
function bA(mdl,n,src,pos), try add_block(src,[mdl '/' n],'Position',pos); catch e, fprintf('  [!] add %s: %s\n',n,e.message); end, end
function setp2(mdl,b,p,v), try set_param([mdl '/' b],p,v); catch, end, end
function ln(mdl,b1,t1,i1,b2,t2,i2)
  try h1=get_param([mdl '/' b1],'PortHandles'); h2=get_param([mdl '/' b2],'PortHandles');
      add_line(mdl,h1.(t1)(i1),h2.(t2)(i2),'autorouting','on');
  catch e, fprintf('  [!] %s.%s(%d)->%s.%s(%d): %s\n',b1,t1,i1,b2,t2,i2,e.message); end
end
