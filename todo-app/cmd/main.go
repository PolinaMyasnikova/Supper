package main

import (
	todo "github.com/PolinaMyasnikova/todo_app"
	"github.com/PolinaMyasnikova/todo_app/pkg/handler"
	"github.com/PolinaMyasnikova/todo_app/pkg/repository"
	service2 "github.com/PolinaMyasnikova/todo_app/pkg/service"
	"log"
)

func main() {
	repos := repository.NewRepository()      //сюда поступают http запросы
	services := service2.NewService(repos)   //потом они прередаются на уровень бизнес логики
	handlers := handler.NewHandler(services) //и уже потом они свзязывася с базой данных
	srv := new(todo.Server)
	if err := srv.Run("8000", handlers.InitRoutes()); err != nil {
		log.Fatalf("error occured while running http server: %s", err.Error())
	}
}
