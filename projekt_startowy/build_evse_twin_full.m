function build_evse_twin_full()
% BUILD_EVSE_TWIN_FULL  Pelny blizniak: FIZYKA (Simscape) + STEROWANIE (Stateflow).
% ------------------------------------------------------------------------
% Dwa obwody Simscape sterowane przez dwie karty Stateflow:
%   (1) Obwod CP (fizyczny dzielnik): DC 12V -> R1 -> CP -> dioda -> R2 -> masa;
%       galaz SW+R3 sterowana StateC (emulator). Voltage Sensor -> cp_voltage.
%       Pilot dajemy jako +12V DC: poziomy 9/6V robi dzielnik (poprawne dla
%       detekcji stanu). duty/PWM = osobny watek (logowany).
%   (2) Tor mocy: AC -> stycznik K -> Isens -> Rload -> masa; licznik energii.
%       K sterowany: close = contactor_cmd AND not(fault_p1).
% Sprzezenia: Emulator.StateC -> SW(CP); CP.Voltage Sensor -> Wzorzec.cp_voltage;
%             Wzorzec.contactor_cmd -> brama -> K; Wzorzec.I_offer -> Emulator.
%
% Pozycje blokow = [left top right bottom]. BooleanDataType=off. Etykiety SF
% parse-safe. NIE rusza istniejacych plikow (cp_circuit, evse_power, v2/v3).
%
% NIE uruchomione u autora. Bloki/parametry/pozycje pewne; OKABLOWANIE FIZYCZNE
% (Simscape, porty .LConn/.RConn) = best-effort -> dokoncz wg [WIRING].
% Iterujemy rundami: odpal, wyslij [!], poprawie.
% ------------------------------------------------------------------------
mdl='evse_twin';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);
try set_param(mdl,'BooleanDataType','off'); catch, end
try set_param(mdl,'StopTime','5'); catch, end

buildEmu(mdl); buildGolden(mdl);
buildCP(mdl); buildPower(mdl);
wireAll(mdl);
try Simulink.BlockDiagram.arrangeSystem(mdl); catch, end
printWiring();
fprintf('\nModel "%s" zbudowany. Dokoncz [WIRING] (Simscape) i Run.\n',mdl);
end

% ===================== KARTY STATEFLOW =====================
function buildEmu(mdl)
nm='Emulator_auta'; ch=getChart(mdl,nm,[40 40 240 200]);
addData(ch,'cmd','Input'); addData(ch,'fault_inject','Input'); addData(ch,'I_offer','Input');
addData(ch,'StateC','Output'); addData(ch,'i_demand','Output');
sA=addState(ch,sprintf('A_Unplugged\nentry: StateC=0; i_demand=0;'),[ 50 60 160 70]);
sB=addState(ch,sprintf('B_Connected\nentry: StateC=0; i_demand=0;'),[260 60 160 70]);
sC=addState(ch,sprintf('C_Ready\nentry: StateC=1; i_demand=min(I_offer,32);'),[470 60 190 80]);
sF=addState(ch,sprintf('Fault\nentry: StateC=0; i_demand=0;'),[260 190 160 70]);
addDefault(ch,sA,0);
addTrans(ch,sA,sB,'[cmd==1]',3,9); addTrans(ch,sB,sC,'[cmd==2]',3,9);
addTrans(ch,sC,sB,'[cmd==3]',10,2); addTrans(ch,sB,sA,'[cmd==0]',8,4); addTrans(ch,sC,sA,'[cmd==0]',7,1);
addTrans(ch,sB,sF,'[fault_inject==1]',6,12); addTrans(ch,sC,sF,'[fault_inject==1]',7,11);
addTrans(ch,sF,sA,'[fault_inject==0]',9,5);
end

function buildGolden(mdl)
nm='Wzorzec_EVSE'; ch=getChart(mdl,nm,[40 280 280 470]);
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

% ===================== OBWOD CP (Simscape) =====================
function buildCP(mdl)
bA(mdl,'Vpilot','fl_lib/Electrical/Electrical Sources/DC Voltage Source',[360 60 410 110]); setp2(mdl,'Vpilot','v0','12');
bA(mdl,'R1cp','fl_lib/Electrical/Electrical Elements/Resistor',[470 60 530 100]); setp2(mdl,'R1cp','R','1000');
bA(mdl,'Dcp','fl_lib/Electrical/Electrical Elements/Diode',[600 110 660 160]);
bA(mdl,'R2cp','fl_lib/Electrical/Electrical Elements/Resistor',[720 110 780 150]); setp2(mdl,'R2cp','R','2740');
bA(mdl,'SWcp','fl_lib/Electrical/Electrical Elements/Switch',[600 200 660 250]);
bA(mdl,'R3cp','fl_lib/Electrical/Electrical Elements/Resistor',[720 200 780 240]); setp2(mdl,'R3cp','R','1300');
bA(mdl,'Vsns_cp','fl_lib/Electrical/Electrical Sensors/Voltage Sensor',[560 60 610 110]);
bA(mdl,'GNDcp','fl_lib/Electrical/Electrical Elements/Electrical Reference',[700 300 760 340]);
bA(mdl,'Solver_cp','nesl_utility/Solver Configuration',[360 300 440 340]);
bA(mdl,'sc2ps_cp','nesl_utility/Simulink-PS Converter',[470 210 510 240]);   % StateC -> SW
bA(mdl,'ps2s_cp','nesl_utility/PS-Simulink Converter',[640 30 685 54]);       % Vsensor -> cp_voltage
bA(mdl,'scCP','simulink/Sinks/Scope',[720 20 760 60]);
end

% ===================== TOR MOCY (Simscape) =====================
function buildPower(mdl)
bA(mdl,'AC','fl_lib/Electrical/Electrical Sources/AC Voltage Source',[360 560 410 620]);
setp2(mdl,'AC','amplitude','325'); setp2(mdl,'AC','frequency','50');
bA(mdl,'K','fl_lib/Electrical/Electrical Elements/Switch',[470 560 530 610]);
bA(mdl,'Isens','fl_lib/Electrical/Electrical Sensors/Current Sensor',[580 555 640 615]);
bA(mdl,'Rload','fl_lib/Electrical/Electrical Elements/Resistor',[700 565 760 605]); setp2(mdl,'Rload','R','14.4');
bA(mdl,'Vsns_p','fl_lib/Electrical/Electrical Sensors/Voltage Sensor',[700 660 760 720]);
bA(mdl,'GNDp','fl_lib/Electrical/Electrical Elements/Electrical Reference',[560 700 620 740]);
bA(mdl,'Solver_p','nesl_utility/Solver Configuration',[360 700 440 740]);
% brama: close = contactor_cmd AND not(fault_p1)  (double -> konwerter)
bA(mdl,'one','simulink/Sources/Constant',[40 560 90 590]); setp2(mdl,'one','Value','1');
bA(mdl,'subF','simulink/Math Operations/Subtract',[150 560 185 595]);   % 1 - fault_p1
bA(mdl,'pClose','simulink/Math Operations/Product',[230 540 265 580]);  % contactor_cmd * notf
bA(mdl,'cl2ps','nesl_utility/Simulink-PS Converter',[300 545 345 575]); % -> K control
% licznik: P=u*i -> calka -> kWh
bA(mdl,'i2s','nesl_utility/PS-Simulink Converter',[660 530 705 554]);
bA(mdl,'v2s','nesl_utility/PS-Simulink Converter',[770 680 815 704]);
bA(mdl,'P','simulink/Math Operations/Product',[860 560 895 600]);
bA(mdl,'Int','simulink/Continuous/Integrator',[940 560 980 600]);
bA(mdl,'gK','simulink/Math Operations/Gain',[1020 560 1060 600]); setp2(mdl,'gK','Gain','1/3.6e6');
bA(mdl,'Disp','simulink/Sinks/Display',[1100 562 1160 588]);
bA(mdl,'scK','simulink/Sinks/Scope',[1100 620 1140 660]);
end

% ===================== OKABLOWANIE =====================
function wireAll(mdl)
% --- sygnaly (pewne) ---
bA(mdl,'cmd','simulink/Sources/Step',[40 200 90 235]);
setp2(mdl,'cmd','Time','2'); setp2(mdl,'cmd','Before','1'); setp2(mdl,'cmd','After','2');
bA(mdl,'finj','simulink/Sources/Constant',[40 250 90 280]); setp2(mdl,'finj','Value','0');
bA(mdl,'auth','simulink/Sources/Constant',[40 470 90 500]); setp2(mdl,'auth','Value','1');
bA(mdl,'Iav','simulink/Sources/Constant',[40 510 90 540]);  setp2(mdl,'Iav','Value','16');
bA(mdl,'fp1','simulink/Sources/Constant',[40 620 90 650]);  setp2(mdl,'fp1','Value','0');
bA(mdl,'Imem','simulink/Discrete/Memory',[150 460 195 490]);
ln(mdl,'cmd','Outport',1,'Emulator_auta','Inport',1);
ln(mdl,'finj','Outport',1,'Emulator_auta','Inport',2);
ln(mdl,'Wzorzec_EVSE','Outport',3,'Imem','Inport',1);
ln(mdl,'Imem','Outport',1,'Emulator_auta','Inport',3);
ln(mdl,'auth','Outport',1,'Wzorzec_EVSE','Inport',2);
ln(mdl,'fp1','Outport',1,'Wzorzec_EVSE','Inport',3);
ln(mdl,'Iav','Outport',1,'Wzorzec_EVSE','Inport',4);
ln(mdl,'fp1','Outport',1,'subF','Inport',2);  ln(mdl,'one','Outport',1,'subF','Inport',1);
ln(mdl,'Wzorzec_EVSE','Outport',2,'pClose','Inport',1);
ln(mdl,'subF','Outport',1,'pClose','Inport',2);
% sprzezenia sygnal->Simscape (przez konwertery)
ln(mdl,'Emulator_auta','Outport',1,'sc2ps_cp','Inport',1);   % StateC -> S2PS(CP)
ln(mdl,'ps2s_cp','Outport',1,'Wzorzec_EVSE','Inport',1);      % cp_voltage -> Wzorzec
ln(mdl,'ps2s_cp','Outport',1,'scCP','Inport',1);
ln(mdl,'pClose','Outport',1,'cl2ps','Inport',1);             % close -> S2PS(power)
ln(mdl,'i2s','Outport',1,'P','Inport',1); ln(mdl,'v2s','Outport',1,'P','Inport',2);
ln(mdl,'P','Outport',1,'Int','Inport',1); ln(mdl,'Int','Outport',1,'gK','Inport',1);
ln(mdl,'gK','Outport',1,'Disp','Inport',1); ln(mdl,'gK','Outport',1,'scK','Inport',1);
% --- Simscape fizyczne (best-effort) ---
W(mdl,'Vpilot','RConn',1,'R1cp','LConn',1);
W(mdl,'R1cp','RConn',1,'Dcp','LConn',1);
W(mdl,'Dcp','RConn',1,'R2cp','LConn',1); W(mdl,'R2cp','RConn',1,'GNDcp','LConn',1);
W(mdl,'Dcp','RConn',1,'SWcp','LConn',1); W(mdl,'SWcp','RConn',1,'R3cp','LConn',1); W(mdl,'R3cp','RConn',1,'GNDcp','LConn',1);
W(mdl,'Vpilot','LConn',1,'GNDcp','LConn',1); W(mdl,'Solver_cp','RConn',1,'GNDcp','LConn',1);
W(mdl,'Vsns_cp','LConn',1,'R1cp','RConn',1); W(mdl,'Vsns_cp','RConn',1,'GNDcp','LConn',1);
W(mdl,'sc2ps_cp','RConn',1,'SWcp','LConn',2); W(mdl,'Vsns_cp','RConn',2,'ps2s_cp','Inport',1);
W(mdl,'AC','RConn',1,'K','LConn',1); W(mdl,'K','RConn',1,'Isens','LConn',1);
W(mdl,'Isens','RConn',1,'Rload','LConn',1); W(mdl,'Rload','RConn',1,'GNDp','LConn',1);
W(mdl,'AC','LConn',1,'GNDp','LConn',1); W(mdl,'Solver_p','RConn',1,'GNDp','LConn',1);
W(mdl,'Vsns_p','LConn',1,'Rload','LConn',1); W(mdl,'Vsns_p','RConn',1,'GNDp','LConn',1);
W(mdl,'cl2ps','RConn',1,'K','LConn',2); W(mdl,'Isens','RConn',2,'i2s','Inport',1); W(mdl,'Vsns_p','RConn',2,'v2s','Inport',1);
end

function printWiring()
fprintf(['\n[WIRING] dokoncz porty fizyczne Simscape (jesli [!]):\n' ...
 ' CP:  Vpilot(+)-R1cp ; R1cp-(CP)-Dcp(anoda) ; Dcp(katoda)-X ; X-R2cp-GND ; X-SWcp-R3cp-GND\n' ...
 '      Vpilot(-)-GND ; Solver_cp-GND ; Vsns_cp(+)-CP, Vsns_cp(-)-GND ; SWcp(sterow.PS)<-sc2ps_cp ; Vsns_cp(I/V PS)->ps2s_cp\n' ...
 ' MOC: AC(+)-K-Isens-Rload-GND ; AC(-)-GND ; Solver_p-GND ; Vsns_p rownolegle do Rload\n' ...
 '      K(sterow.PS)<-cl2ps ; Isens(I,PS)->i2s ; Vsns_p(V,PS)->v2s\n']);
end

% ===================== HELPERY =====================
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
  catch e, fprintf('  [!] sig %s.%s(%d)->%s.%s(%d): %s\n',b1,t1,i1,b2,t2,i2,e.message); end
end
function W(mdl,b1,t1,i1,b2,t2,i2)
  try h1=get_param([mdl '/' b1],'PortHandles'); h2=get_param([mdl '/' b2],'PortHandles');
      add_line(mdl,h1.(t1)(i1),h2.(t2)(i2),'autorouting','on');
  catch e, fprintf('  [!] phys %s.%s(%d)->%s.%s(%d): %s\n',b1,t1,i1,b2,t2,i2,e.message); end
end
