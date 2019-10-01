
angular.module("epsonEditor", []);

angular.module("epsonEditor").controller("epsonCtrl", ['$scope', '$http', function($scope, $http) {
    $scope.app = "ASC WebServer";

    $scope.serverIp = "";

    $scope.amqpKey = "";
    $scope.rabbitmqLogin = "";
    $scope.rabbitmqPassword = "";

    $scope.lwm2mServerIp = "";
    $scope.lwm2mBootstrapIp = "";
    $scope.lwm2mDtlsEnable = "";
    $scope.lwm2mDtlsIdentity = "";
    $scope.lwm2mDtlsKey = "";

    $scope.wifiEnable = "";
    $scope.wifiSsid = "";
    $scope.wifiPsk = "";

    $scope.sendConfig = function () {

        hideAlerts();

        message = {
            serverIp: $scope.serverIp,
            amqpKey: $scope.amqpKey,
            rabbitmqLogin: $scope.rabbitmqLogin,
            rabbitmqPassword: $scope.rabbitmqPassword,        
            lwm2mServerIp: $scope.lwm2mServerIp,
            lwm2mBootstrapIp: $scope.lwm2mBootstrapIp,
            lwm2mDtlsEnable: $scope.lwm2mDtlsEnable,
            lwm2mDtlsIdentity: $scope.lwm2mDtlsIdentity,
            lwm2mDtlsKey: $scope.lwm2mDtlsKey,
            wifiEnable: $scope.wifiEnable,
            wifiSsid: $scope.wifiSsid,
            wifiPsk: $scope.wifiPsk
        }

        $http.post("/setconfig", message).then(function (result) {

            console.log(result.data)

            if (result.data.result == "success") {
                showSuccess("Configurações feitas com sucesso.")
            }
            else {
                showError("Configuração inválida!" + result.data.message)
            }            
        });
    };

    hideAlerts = function () {
        var x = document.getElementById("alert_success");
        x.style.display = "none";

        var x = document.getElementById("alert_error");
        x.style.display = "none";
    }

    showSuccess = function (message) {
        var x = document.getElementById("alert_success");
        x.innerHTML = "<strong>Sucesso! </strong>" + message;   
        x.style.display = "block";
    }

    showError = function (message) {
        var x = document.getElementById("alert_error");
        x.innerHTML = "<strong>Erro! </strong>" + message;
        x.style.display = "block";
    }

    getConfig = function () {
        $http.get("/getconfig", {}).then(function (result) {
            config = result.data;
            console.log(config)

            if (config.result == "success") {
                $scope.serverIp = config.server_ip;
                $scope.rabbitmqLogin = config.rabbitmq_login;

                $scope.lwm2mServerIp = config.lwm2m_server_ip;
                $scope.lwm2mBootstrapIp = config.lwm2m_bootstrap_ip;
                $scope.lwm2mDtlsEnable = config.lwm2m_dtls_enable;
                $scope.lwm2mDtlsIdentity = config.lwm2m_dtls_identity;

                $scope.wifiEnable = config.wifi_enable;
                $scope.wifiSsid = config.wifi_ssid;
            }
            else {
                showError("Não foi possível receber os dados!")
            }
            
        });
    };

    getConfig();

}]);
