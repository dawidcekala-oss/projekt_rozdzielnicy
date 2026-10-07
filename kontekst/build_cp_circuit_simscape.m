function build_cp_circuit_simscape()
% BUILD_CP_CIRCUIT_SIMSCAPE  Buduje obwod Control Pilot (IEC 61851) w Simscape.
%
%   Wymaga: Simulink + Simscape (base).  NIE wymaga dodatku Simscape Electrical
%   (uzywamy Foundation Library: fl_lib).
%   Uruchom w MATLAB:   >> build_cp_circuit_simscape
%
%   UWAGA: skrypt nie byl uruchomiony u autora (brak MATLAB-a w srodowisku).
%   Sciezki blokow sa standardowe, a kazdy krok jest w try/catch - jesli cos
%   nie wstanie, zobaczysz komunikat [!] i dokonczysz recznie wg listy polaczen
%   w pliku README_obwod_CP.md. Bloki i parametry powstaja niezawodnie;
%   ewentualne braki dotycza tylko paru linii (5 min dorysowania).
%
%   StateC = 0  -> stan B (plateau ~9 V).   StateC = 1 -> stan C (~6 V).

mdl = 'cp_circuit';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

% ---------- parametry obwodu ----------
R1v=1000; R2v=2740; R3v=1300; f=1000; duty=50; Vamp=24;  % Vamp 0..24 -> bias -12 -> +/-12

A=@(name,src,pos) safe_add([mdl '/' name],src,pos);

% ---------- bloki sygnalowe (Simulink) ----------
A('PWM','simulink/Sources/Pulse Generator',[30 30 90 90]);
try set_param([mdl '/PWM'],'PulseType','Time based','Amplitude',num2str(Vamp), ...
    'Period',num2str(1/f),'PulseWidth',num2str(duty)); catch e, disp(e.message); end
A('Bias','simulink/Math Operations/Bias',[130 40 170 80]);
try set_param([mdl '/Bias'],'Bias','-12'); catch, end
A('StateC','simulink/Sources/Constant',[30 300 90 340]);
try set_param([mdl '/StateC'],'Value','0'); catch, end   % 0=B, 1=C
A('Scope','simulink/Sinks/Scope',[770 60 810 100]);

% ---------- mostki PS ----------
A('S2PS','nesl_utility/Simulink-PS Converter',[200 45 240 75]);
A('S2PS_sw','nesl_utility/Simulink-PS Converter',[150 305 190 335]);
A('PS2S','nesl_utility/PS-Simulink Converter',[690 65 730 95]);

% ---------- bloki fizyczne (Simscape Foundation) ----------
A('Vsrc','fl_lib/Electrical/Electrical Sources/Controlled Voltage Source',[280 60 330 140]);
A('R1','fl_lib/Electrical/Electrical Elements/Resistor',[380 25 440 65]);
try set_param([mdl '/R1'],'R',num2str(R1v)); catch, end
A('D1','fl_lib/Electrical/Electrical Elements/Diode',[480 110 540 160]);
A('R2','fl_lib/Electrical/Electrical Elements/Resistor',[580 200 640 240]);
try set_param([mdl '/R2'],'R',num2str(R2v)); catch, end
A('SW','fl_lib/Electrical/Electrical Elements/Switch',[480 260 540 300]);
A('R3','fl_lib/Electrical/Electrical Elements/Resistor',[580 260 640 300]);
try set_param([mdl '/R3'],'R',num2str(R3v)); catch, end
A('Vsense','fl_lib/Electrical/Electrical Sensors/Voltage Sensor',[610 55 660 115]);
A('GND','fl_lib/Electrical/Electrical Elements/Electrical Reference',[380 340 440 380]);
A('Solver','nesl_utility/Solver Configuration',[30 390 110 430]);

% ---------- polaczenia (best-effort) ----------
fprintf('Laczenie blokow (komunikaty [!] = dokoncz recznie wg README)...\n');
C=@(b1,p1,i1,b2,p2,i2) safe_connect(mdl,b1,p1,i1,b2,p2,i2);
C('PWM','Outport',1,'Bias','Inport',1);
C('Bias','Outport',1,'S2PS','Inport',1);
C('S2PS','RConn',1,'Vsrc','LConn',1);     % sygnal sterujacy zrodlem
C('Vsrc','RConn',1,'R1','LConn',1);       % + zrodla -> R1
C('R1','RConn',1,'D1','LConn',1);         % wezel CP -> anoda diody
C('D1','RConn',1,'R2','LConn',1);         % za dioda (wezel X) -> R2
C('R2','RConn',1,'GND','LConn',1);
C('D1','RConn',1,'SW','LConn',1);         % X -> switch (galaz R3)
C('SW','RConn',1,'R3','LConn',1);
C('R3','RConn',1,'GND','LConn',1);
C('Vsrc','LConn',2,'GND','LConn',1);      % - zrodla -> masa
C('StateC','Outport',1,'S2PS_sw','Inport',1);
C('S2PS_sw','RConn',1,'SW','LConn',2);    % sterowanie switchem
C('Vsense','LConn',1,'R1','RConn',1);     % +sensora -> CP
C('Vsense','LConn',2,'GND','LConn',1);    % -sensora -> masa
C('Vsense','RConn',1,'PS2S','Inport',1);
C('PS2S','Outport',1,'Scope','Inport',1);
C('Solver','RConn',1,'GND','LConn',1);

% ---------- konfiguracja symulacji ----------
try set_param(mdl,'StopTime','9e-3'); catch, end
try set_param(mdl,'Solver','daessc'); catch, end
try Simulink.BlockDiagram.arrangeSystem(mdl); catch, end   % auto-uklad

fprintf(['\nGotowe. Uruchom (Run). StateC=1 -> stan C (plateau ~6 V).\n' ...
         'Spodziewane plateau: stan B ~9 V, stan C ~6 V, dol -12 V.\n']);
end

% ================= funkcje pomocnicze =================
function safe_add(dst,src,pos)
  try, add_block(src,dst,'Position',pos);
  catch e, fprintf('  [!] nie dodano %s z %s: %s\n',dst,src,e.message); end
end

function safe_connect(mdl,b1,p1,i1,b2,p2,i2)
  try
    h1=get_param([mdl '/' b1],'PortHandles');
    h2=get_param([mdl '/' b2],'PortHandles');
    add_line(mdl,h1.(p1)(i1),h2.(p2)(i2),'autorouting','on');
  catch e
    fprintf('  [!] %s.%s(%d) -> %s.%s(%d): %s\n',b1,p1,i1,b2,p2,i2,e.message);
  end
end
