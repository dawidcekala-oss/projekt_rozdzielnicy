function build_evse_simulink()
% BUILD_EVSE_SIMULINK
% Tworzy w Simulinku: (A) dwie karty Stateflow przez Stateflow API,
% (B) bloki toru mocy (Simscape) + wypisuje liste polaczen do dorysowania.
%
% Uruchom w MATLAB:  >> build_evse_simulink
% UWAGA: skrypt NIE byl uruchomiony u autora (brak MATLAB-a) -> moga byc
% drobne roznice wersyjne. Kazda sekcja w try/catch i wypisuje [OK]/[!].
% Iterujemy: odpal, wyslij komunikat bledu / zrzut, poprawie.
%
% Wymaga: Simulink + Stateflow (+ Simscape do sekcji toru mocy).

mdl = 'evse_model';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

build_emulator(mdl);     % karta Stateflow: samochod (aktor)
build_wzorzec(mdl);      % karta Stateflow: zloty wzorzec EVSE (aktor)
build_powerpath(mdl);    % bloki Simscape toru mocy + lista polaczen

try, Simulink.BlockDiagram.arrangeSystem(mdl); catch, end
fprintf('\nGotowe. Otwórz karty Stateflow (dwuklik) i sprawdz stany/przejscia.\n');
fprintf('Tor mocy: dokoncz polaczenia wg listy [POWER WIRING] wyzej.\n');
end

% ================= STATEFLOW: helpery =================
function ch = getChart(mdl,name)
  add_block('sflib/Chart',[mdl '/' name]);
  rt = sfroot;
  ch = rt.find('-isa','Stateflow.Chart','-and','Name',name);
  if numel(ch)>1, ch = ch(end); end
end
function d = sfData(ch,name,scope)
  d = Stateflow.Data(ch); d.Name = name; d.Scope = scope;
end
function s = sfState(ch,label,pos)
  s = Stateflow.State(ch); s.LabelString = label; s.Position = pos;
end
function t = sfTrans(ch,src,dst,cond)
  t = Stateflow.Transition(ch); t.Source = src; t.Destination = dst;
  if ~isempty(cond), t.LabelString = ['[' cond ']']; end
end
function sfDefault(ch,s)   % domyslne przejscie wejsciowe do stanu s
  t = Stateflow.Transition(ch); t.Destination = s;
  p = s.Position; t.DestinationOClock = 0;
  t.SourceEndPoint = [p(1)+p(3)/2, p(2)-28];
  t.MidPoint       = [p(1)+p(3)/2, p(2)-14];
end

% ================= KARTA 1: Emulator auta =================
function build_emulator(mdl)
try
  nm = 'Emulator_auta';
  ch = getChart(mdl,nm);
  % dane (porty)
  sfData(ch,'cmd','Input');           % 0=unplug,1=connect,2=ready,3=stop
  sfData(ch,'fault_inject','Input');  % 1=wstrzyknij usterke
  sfData(ch,'StateC','Output');       % 0=stan B, 1=stan C (dolacza R3)
  sfData(ch,'diode_on','Output');     % 1=dioda wpieta (brak=usterka)
  sfData(ch,'i_demand','Output');     % prad pobierany w stanie C [A]
  % stany
  sA = sfState(ch, sprintf('A_Unplugged\nen: StateC=0; diode_on=0; i_demand=0;'), [ 30  40 160 70]);
  sB = sfState(ch, sprintf('B_Connected\nen: diode_on=1; StateC=0; i_demand=0;'), [260  40 160 70]);
  sC = sfState(ch, sprintf('C_Ready\nen: StateC=1; i_demand=16;'),                [490  40 160 70]);
  sF = sfState(ch, sprintf('Fault\nen: diode_on=0;'),                            [260 180 160 70]);
  sfDefault(ch,sA);
  sfTrans(ch,sA,sB,'cmd==1');   % connect
  sfTrans(ch,sB,sC,'cmd==2');   % ready
  sfTrans(ch,sC,sB,'cmd==3');   % stop
  sfTrans(ch,sB,sA,'cmd==0');   % unplug
  sfTrans(ch,sB,sF,'fault_inject==1');
  sfTrans(ch,sF,sA,'fault_inject==0');
  fprintf('[OK] karta %s\n',nm);
catch e, fprintf('[!] Emulator_auta: %s\n',e.message); end
end

% ================= KARTA 2: Zloty wzorzec EVSE =================
% Rdzen 3 petli w jednej karcie wykluczajacej:
%   petla 2 (sterowanie) = Idle/Detected/Charging
%   petla 1 (bezpieczenstwo) = Tripped (nadrzedne weto, [fault_p1])
%   petla 3 (aplikacja) = dane wejsciowe auth_ok / limit_p3
function build_wzorzec(mdl)
try
  nm = 'Wzorzec_EVSE';
  ch = getChart(mdl,nm);
  sfData(ch,'cp_voltage','Input');    % napiecie CP [V] (jedyne z granicy)
  sfData(ch,'auth_ok','Input');       % petla 3: autoryzacja (RFID/limit)
  sfData(ch,'fault_p1','Input');      % petla 1: usterka (RCD/PE/zwarcie/...)
  sfData(ch,'I_avail','Input');       % limit pradu (instalacja/DLB/PP) [A]
  sfData(ch,'duty','Output');         % wypelnienie PWM [%]
  sfData(ch,'contactor_cmd','Output');% zadanie zamkniecia stycznika
  sfData(ch,'I_offer','Output');      % prad oferowany [A]
  % stany (petla 2 + Tripped)
  sIdle = sfState(ch, sprintf('Idle\n(widzi A, +12V)\nen: contactor_cmd=0; duty=100;'),                 [ 30  40 180 80]);
  sDet  = sfState(ch, sprintf('Detected\n(widzi B, ~9V)\nen: I_offer=I_avail; duty=I_offer/0.6; contactor_cmd=0;'),[280 40 200 90]);
  sChg  = sfState(ch, sprintf('Charging\n(widzi C, ~6V)\nen: contactor_cmd=1;'),                         [540  40 180 80]);
  sTrip = sfState(ch, sprintf('Tripped\n(weto petli 1)\nen: contactor_cmd=0; duty=100;'),                [280 200 200 80]);
  sfDefault(ch,sIdle);
  % petla 2 (handshake) wg progow napiecia CP
  sfTrans(ch,sIdle,sDet,'cp_voltage>7.5 && cp_voltage<10.5');
  sfTrans(ch,sDet,sChg,'cp_voltage>4.5 && cp_voltage<7.5 && auth_ok==1');
  sfTrans(ch,sChg,sDet,'cp_voltage>7.5 && cp_voltage<10.5');
  sfTrans(ch,sDet,sIdle,'cp_voltage>10.5');
  sfTrans(ch,sChg,sIdle,'cp_voltage>10.5');
  % petla 1 (weto) — z kazdego stanu do Tripped
  sfTrans(ch,sIdle,sTrip,'fault_p1==1');
  sfTrans(ch,sDet,sTrip,'fault_p1==1');
  sfTrans(ch,sChg,sTrip,'fault_p1==1');
  sfTrans(ch,sTrip,sIdle,'fault_p1==0');
  fprintf('[OK] karta %s\n',nm);
catch e, fprintf('[!] Wzorzec_EVSE: %s\n',e.message); end
end

% ================= TOR MOCY (Simscape) =================
function build_powerpath(mdl)
try
  A=@(n,src,pos) safeAdd([mdl '/' n],src,pos);
  A('AC_src','fl_lib/Electrical/Electrical Sources/AC Voltage Source',[40 360 100 420]);
  A('K_stycznik','fl_lib/Electrical/Electrical Elements/Switch',     [200 360 260 410]);
  A('I_sensor','fl_lib/Electrical/Electrical Sensors/Current Sensor',[320 360 380 410]);
  A('Load','fl_lib/Electrical/Electrical Sources/Controlled Current Source',[460 360 520 420]);
  A('GND_pwr','fl_lib/Electrical/Electrical Elements/Electrical Reference',[200 470 260 510]);
  A('Solver_pwr','nesl_utility/Solver Configuration',[40 470 120 510]);
  % licznik energii (Simulink): P=U*I -> calka -> kWh
  A('I_ps','nesl_utility/PS-Simulink Converter',[400 360 440 390]);
  A('Umeas','simulink/Sources/Constant',[460 300 520 330]); set_param([mdl '/Umeas'],'Value','230');
  A('P','simulink/Math Operations/Product',[560 320 600 360]);
  A('Int','simulink/Continuous/Integrator',[630 320 670 360]);
  A('kWh','simulink/Math Operations/Gain',[700 320 740 360]); set_param([mdl '/kWh'],'Gain','1/3.6e6');
  A('E_scope','simulink/Sinks/Scope',[780 320 820 360]);
  % brama stycznika: contactor_cmd AND not(fault) -> sterowanie K
  A('cmd_in','simulink/Sources/Constant',[40 250 100 280]); set_param([mdl '/cmd_in'],'Value','1');
  A('fault_in','simulink/Sources/Constant',[40 300 100 330]); set_param([mdl '/fault_in'],'Value','0');
  A('NOTf','simulink/Logic and Bit Operations/Logical Operator',[140 295 180 325]); set_param([mdl '/NOTf'],'Operator','NOT');
  A('ANDg','simulink/Logic and Bit Operations/Logical Operator',[210 270 250 300]); set_param([mdl '/ANDg'],'Operator','AND');
  A('gate_ps','nesl_utility/Simulink-PS Converter',[270 275 310 305]);
  fprintf('[OK] bloki toru mocy dodane.\n');
  fprintf(['\n[POWER WIRING] dokoncz polaczenia (Simscape = porty fizyczne):\n' ...
    '  AC_src(+) -> K_stycznik(L) ; K_stycznik(R) -> I_sensor(+) ; I_sensor(-) -> Load(+)\n' ...
    '  Load(-) -> GND ; AC_src(-) -> GND ; Solver_pwr -> GND\n' ...
    '  K_stycznik(sterowanie PS) <- gate_ps ; I_sensor(I, PS) -> I_ps -> P\n' ...
    '  Umeas -> P ; P -> Int -> kWh -> E_scope\n' ...
    '  cmd_in -> ANDg(1) ; fault_in -> NOTf -> ANDg(2) ; ANDg -> gate_ps\n' ...
    '  (docelowo cmd_in = contactor_cmd z karty Wzorzec, fault_in = fault_p1)\n']);
catch e, fprintf('[!] tor mocy: %s\n',e.message); end
end

function safeAdd(dst,src,pos)
  try, add_block(src,dst,'Position',pos);
  catch e, fprintf('  [!] nie dodano %s (%s): %s\n',dst,src,e.message); end
end
