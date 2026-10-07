function build_evse_full()
% BUILD_EVSE_FULL  Zintegrowany blizniak (poziom behawioralny).
% ------------------------------------------------------------------------
% Petla zamknieta:  Emulator_auta --(cp_out=napiecie CP)--> Wzorzec_EVSE
%                   Wzorzec --(I_offer)--> Emulator ; Wzorzec --(contactor_cmd)
%                   --> behawioralny licznik energii (kWh).
% CP jest tu modelowane behawioralnie (emulator wystawia cp_out = 12/9/6/3/0 V),
% wiec petla jest czysto sygnalowa (niezawodne okablowanie). Szczegolowe modele
% FIZYCZNE zostaja osobno: cp_circuit (warstwa CP) i evse_power (tor mocy).
% NIE rusza zadnych istniejacych plikow.
%
% NIE uruchomione u autora (brak MATLAB). Okablowanie sygnalowe = niskie ryzyko,
% ale moze wymagac drobnej iteracji. Odpal -> wyslij komunikat -> poprawie.
% ------------------------------------------------------------------------
mdl='evse_full';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);
try set_param(mdl,'BooleanDataType','off'); catch, end
try set_param(mdl,'StopTime','5'); catch, end

buildEmu(mdl);      % chart Emulator_auta  (In: cmd,fault_inject,I_offer | Out: cp_out,StateC,i_demand)
buildGolden(mdl);   % chart Wzorzec_EVSE   (In: cp_voltage,auth_ok,fault_p1,I_avail | Out: duty,contactor_cmd,I_offer,pwm_on)

% --- zrodla scenariusza / nastawy ---
bA(mdl,'cmd','simulink/Sources/Step',[40 60 90 95]);
setp2(mdl,'cmd','Time','2'); setp2(mdl,'cmd','Before','1'); setp2(mdl,'cmd','After','2'); % 1=connect ->(t=2) 2=ready
bA(mdl,'finj','simulink/Sources/Constant',[40 120 90 150]); setp2(mdl,'finj','Value','0'); % fault_inject auta
bA(mdl,'auth','simulink/Sources/Constant',[40 210 90 240]); setp2(mdl,'auth','Value','1'); % auth_ok
bA(mdl,'Iav','simulink/Sources/Constant',[40 260 90 290]);  setp2(mdl,'Iav','Value','16');  % I_avail [A]
bA(mdl,'fp1','simulink/Sources/Constant',[40 320 90 350]);  setp2(mdl,'fp1','Value','0');   % fault_p1 (ustaw 1 = weto)
bA(mdl,'Imem','simulink/Discrete/Memory',[300 150 345 185]);  % przerywa petle algebraiczna I_offer

% --- behawioralny licznik energii ---
bA(mdl,'one','simulink/Sources/Constant',[620 340 660 370]); setp2(mdl,'one','Value','1');
bA(mdl,'sub','simulink/Math Operations/Subtract',[700 305 735 340]);  % 1 - fault_p1 = notf
bA(mdl,'pCl','simulink/Math Operations/Product',[780 255 815 295]);   % contactor_cmd * notf = close
bA(mdl,'pLd','simulink/Math Operations/Product',[860 255 895 295]);   % close * I_offer = I_load
bA(mdl,'gV','simulink/Math Operations/Gain',[940 260 980 290]); setp2(mdl,'gV','Gain','230'); % P=230*I
bA(mdl,'Int','simulink/Continuous/Integrator',[1020 260 1060 290]);
bA(mdl,'gK','simulink/Math Operations/Gain',[1100 260 1140 290]); setp2(mdl,'gK','Gain','1/3.6e6');
bA(mdl,'Disp','simulink/Sinks/Display',[1180 262 1245 288]);
bA(mdl,'scK','simulink/Sinks/Scope',[1180 330 1220 370]);
bA(mdl,'scCP','simulink/Sinks/Scope',[300 60 340 100]);   % podglad cp_voltage
bA(mdl,'scC','simulink/Sinks/Scope',[780 120 820 160]);   % podglad contactor_cmd

% --- okablowanie (sygnaly double) ---
ln(mdl,'cmd','Outport',1,'Emulator_auta','Inport',1);
ln(mdl,'finj','Outport',1,'Emulator_auta','Inport',2);
ln(mdl,'Wzorzec_EVSE','Outport',3,'Imem','Inport',1);     % I_offer -> Memory
ln(mdl,'Imem','Outport',1,'Emulator_auta','Inport',3);    % -> Emulator I_offer
ln(mdl,'Emulator_auta','Outport',1,'Wzorzec_EVSE','Inport',1); % cp_out -> cp_voltage
ln(mdl,'Emulator_auta','Outport',1,'scCP','Inport',1);
ln(mdl,'auth','Outport',1,'Wzorzec_EVSE','Inport',2);
ln(mdl,'fp1','Outport',1,'Wzorzec_EVSE','Inport',3);
ln(mdl,'Iav','Outport',1,'Wzorzec_EVSE','Inport',4);
% brama: close = contactor_cmd * (1 - fault_p1)
ln(mdl,'one','Outport',1,'sub','Inport',1);
ln(mdl,'fp1','Outport',1,'sub','Inport',2);
ln(mdl,'Wzorzec_EVSE','Outport',2,'pCl','Inport',1);
ln(mdl,'sub','Outport',1,'pCl','Inport',2);
ln(mdl,'Wzorzec_EVSE','Outport',2,'scC','Inport',1);
% I_load = close * I_offer ; P=230*I ; E=int ; kWh
ln(mdl,'pCl','Outport',1,'pLd','Inport',1);
ln(mdl,'Wzorzec_EVSE','Outport',3,'pLd','Inport',2);
ln(mdl,'pLd','Outport',1,'gV','Inport',1);
ln(mdl,'gV','Outport',1,'Int','Inport',1);
ln(mdl,'Int','Outport',1,'gK','Inport',1);
ln(mdl,'gK','Outport',1,'Disp','Inport',1);
ln(mdl,'gK','Outport',1,'scK','Inport',1);

try Simulink.BlockDiagram.arrangeSystem(mdl); catch, end
fprintf(['Model "%s" zbudowany. Run: cmd-step prowadzi A->B->C, Wzorzec oferuje prad,\n' ...
         'stycznik zamyka tor, licznik liczy kWh. Ustaw fp1=1 -> weto (energia staje).\n'], mdl);
end

% ================= KARTY STATEFLOW =================
function buildEmu(mdl)
nm='Emulator_auta'; ch=getChart(mdl,nm,[140 40 360 200]);
addData(ch,'cmd','Input'); addData(ch,'fault_inject','Input'); addData(ch,'I_offer','Input');
addData(ch,'cp_out','Output'); addData(ch,'StateC','Output'); addData(ch,'i_demand','Output');
sA=addState(ch,sprintf('A_Unplugged\nentry: cp_out=12; StateC=0; i_demand=0;'),[ 60 70 180 80]);
sB=addState(ch,sprintf('B_Connected\nentry: cp_out=9; StateC=0; i_demand=0;'), [300 70 180 80]);
sC=addState(ch,sprintf('C_Ready\nentry: cp_out=6; StateC=1; i_demand=min(I_offer,32);'),[540 70 200 90]);
sD=addState(ch,sprintf('D_Vent\nentry: cp_out=3; StateC=1; i_demand=min(I_offer,32);'),[540 210 200 90]);
sF=addState(ch,sprintf('Fault\nentry: cp_out=0; StateC=0; i_demand=0;'),[300 210 180 80]);
addDefault(ch,sA,0);
addTrans(ch,sA,sB,'[cmd==1]',3,9); addTrans(ch,sB,sC,'[cmd==2]',3,9);
addTrans(ch,sC,sB,'[cmd==3]',10,2); addTrans(ch,sC,sD,'[cmd==4]',6,12); addTrans(ch,sD,sC,'[cmd==2]',9,6);
addTrans(ch,sB,sA,'[cmd==0]',8,4); addTrans(ch,sC,sA,'[cmd==0]',7,1); addTrans(ch,sD,sA,'[cmd==0]',7,4);
addTrans(ch,sB,sF,'[fault_inject==1]',6,12); addTrans(ch,sC,sF,'[fault_inject==1]',7,11);
addTrans(ch,sF,sA,'[fault_inject==0]',9,5);
end

function buildGolden(mdl)
nm='Wzorzec_EVSE'; ch=getChart(mdl,nm,[140 330 360 520]);
addData(ch,'cp_voltage','Input'); addData(ch,'auth_ok','Input'); addData(ch,'fault_p1','Input'); addData(ch,'I_avail','Input');
addData(ch,'duty','Output'); addData(ch,'contactor_cmd','Output'); addData(ch,'I_offer','Output'); addData(ch,'pwm_on','Output');
sOp=addState(ch,'Operating',[40 70 900 360]);
sIdle=addState(ch,sprintf('Idle\nentry: pwm_on=0; duty=0; contactor_cmd=0; I_offer=0;'),[ 90 170 210 120]);
sDet =addState(ch,sprintf('Detected\nentry: pwm_on=1; I_offer=I_avail; duty=max(10,min(85,I_offer/0.6)); contactor_cmd=0;'),[380 170 250 150]);
sChg =addState(ch,sprintf('Charging\nentry: contactor_cmd=1;\nduring: I_offer=I_avail; duty=max(10,min(85,I_offer/0.6));'),[710 170 210 130]);
sVent=addState(ch,sprintf('Ventilation\nentry: contactor_cmd=1;'),[710 320 210 90]);
addDefault(ch,sIdle,0);
addTrans(ch,sIdle,sDet,'[cp_voltage>7.5 && cp_voltage<10.5 && I_avail>0]',3,9);
addTrans(ch,sDet,sChg,'[cp_voltage>4.5 && cp_voltage<7.5 && auth_ok==1]',3,9);
addTrans(ch,sChg,sDet,'[cp_voltage>7.5 && cp_voltage<10.5]',11,1);
addTrans(ch,sDet,sIdle,'[cp_voltage>10.5]',8,4);
addTrans(ch,sChg,sVent,'[cp_voltage>1.5 && cp_voltage<4.5]',6,12);
addTrans(ch,sVent,sChg,'[cp_voltage>4.5 && cp_voltage<7.5]',9,6);
sTrip=addState(ch,sprintf('Tripped\nentry: contactor_cmd=0; pwm_on=0; duty=0;'),[380 500 250 110]);
addTrans(ch,sOp,sTrip,'[fault_p1==1 || cp_voltage<1.5]',6,12);
addTrans(ch,sTrip,sOp,'[fault_p1==0 && cp_voltage>1.5]',9,7);
end

% ================= HELPERY =================
function ch=getChart(mdl,name,pos)
  add_block('sflib/Chart',[mdl '/' name],'Position',pos);
  rt=sfroot; cs=rt.find('-isa','Stateflow.Chart'); ch=[];
  for k=1:numel(cs), if strcmp(cs(k).Name,name), ch=cs(k); end, end
end
function d=addData(ch,name,scope), d=Stateflow.Data(ch); d.Name=name; d.Scope=scope; end
function s=addState(ch,label,pos), s=Stateflow.State(ch); s.LabelString=label; s.Position=pos; end
function t=addTrans(ch,src,dst,lbl,sClk,dClk)
  t=Stateflow.Transition(ch); t.Source=src; t.Destination=dst;
  if ~isempty(lbl), t.LabelString=lbl; end
  if nargin>=5&&~isempty(sClk), try t.SourceOClock=sClk; catch, end, end
  if nargin>=6&&~isempty(dClk), try t.DestinationOClock=dClk; catch, end, end
end
function addDefault(ch,dst,clk)
  t=Stateflow.Transition(ch); t.Destination=dst; p=dst.Position;
  try t.DestinationOClock=clk; catch, end
  try t.SourceEndPoint=[p(1)+p(3)/2, p(2)-32]; catch, end
  try t.MidPoint=[p(1)+p(3)/2, p(2)-16]; catch, end
end
function bA(mdl,n,src,pos)
  try add_block(src,[mdl '/' n],'Position',pos); catch e, fprintf('  [!] add %s: %s\n',n,e.message); end
end
function setp2(mdl,blk,par,val), try set_param([mdl '/' blk],par,val); catch, end, end
function ln(mdl,b1,t1,i1,b2,t2,i2)
  try
    h1=get_param([mdl '/' b1],'PortHandles'); h2=get_param([mdl '/' b2],'PortHandles');
    add_line(mdl,h1.(t1)(i1),h2.(t2)(i2),'autorouting','on');
  catch e, fprintf('  [!] %s.%s(%d)->%s.%s(%d): %s\n',b1,t1,i1,b2,t2,i2,e.message); end
end
